import os
from PIL import Image,ImageDraw,ImageFont
from hoshino.util import pic2b64
from ..priconne import chara

PATH = f'{os.path.dirname(os.path.abspath(__file__))}/assests'
FONT = ImageFont.truetype(f'{PATH}/font.ttf', size=12) #该字体的渲染大小为(9,13)

def generateImg(data: list):
    num = len(data)
    icon_size = 48
    canvas = Image.new('RGBA', (icon_size*5,num*(icon_size+13)), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    #处理数据
    for i in range(0, num):
        tag = data[i]["sn"]
        damage = data[i]["damage"]
        remain = data[i]["remain"] if data[i]["remain"] !=0 else ""
        party_tip = f"{tag} {damage}万" #队伍id伤害
        if remain !="":
            party_tip += " 补偿刀"     
    #画图
        units = [chara.fromid(i) for i in data[i]["unit"]]
        party_img = chara.gen_team_pic(units, icon_size, star_slot_verbose=False)
        canvas.paste(party_img,(0,13+i*(icon_size+13)))
        draw.multiline_text((0,i*(icon_size+13)), party_tip, font=FONT, fill="black")
    return pic2b64(canvas)