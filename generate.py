import os
from PIL import Image,ImageDraw,ImageFont
from ..priconne import chara

PATH = f'{os.path.dirname(os.path.abspath(__file__))}'
FONT_PATH = f'{PATH}/assests/font.ttf'

'''
bg的留白共1468x1399px。左起始点34px
两列时，icon_size=128px，单列640px共1280px，三间隔共188px。
三列时，icon_size=86px，单列430px共1290px，四间隔共178px。
四列时，icon_size=64px，单列320px共1280px，五间隔共188px。
'''
def generateImg(data: list, boss_id, date): 
    num = len(data)
    #   根据数据量调整绘制参数
    col_overflow = 1355
    col_interval = 20
    posy = 122
    if num < 16:
        text_size = 19
        text_font = ImageFont.truetype(FONT_PATH, size=18)
        text_overflow = 66
        colnum = 8
        icon_size = 128
        posx = 97
        row_interval = 62
    elif num < 32:
        text_size = 17
        text_font = ImageFont.truetype(FONT_PATH, size=16)
        text_overflow = 48
        colnum = 11
        icon_size = 86
        posx = 79
        row_interval = 44
    else:
        text_size = 13
        text_font = ImageFont.truetype(FONT_PATH, size=12)
        text_overflow = 48
        colnum = 14
        icon_size = 64
        posx = 72
        row_interval = 37
    base = Image.open(f'{PATH}/assests/bg.png')
    draw = ImageDraw.Draw(base)
    # 右上信息
    stage_id = boss_id%4+1
    boss = boss_id//4+1
    draw.text(
        (1214,50), 
        f'{date} {stage_id}阶段{boss}王', 
        (96,114,168), 
        ImageFont.truetype(f'{PATH}/assests/font.ttf', size=36),
        'mm'
    )
    # 处理数据
    total_text_line = 0
    count = 0
    mode_tip = False
    for i in range(0, num):
        # 已达到4列的最大条目数
        if count == 55:
            mode_tip = True
        tag = data[i]["sn"]
        damage = data[i]["damage"]
        party_tip = f"{tag} {damage}万" #队伍id伤害
        if data[i]["remain"] !=0:
            party_tip += '补偿刀'
        info = data[i]["info"] if data[i]["info"] !="" else False
        #队伍含有特殊说明时进行换行处理
        if info:
            party_tip += ' 说明：'
            text_bytes = party_tip.encode('gbk')+info.encode('gbk')
            if len(text_bytes) <= text_overflow:
                party_tip += f"{info}"
                text_newline = 1    #本条文字有几行
            else:
                party_tip = ''
                text_newline = len(text_bytes) // text_overflow +1
                for j in range(0, text_newline):
                    if j == 0:
                        try:
                            msg = text_bytes[:(j+1)*text_overflow]
                            msg = msg.decode('gbk')
                            method = 0
                        except:
                            msg = text_bytes[:(j+1)*text_overflow+1]
                            msg = msg.decode('gbk')
                            method = 1
                    else:
                        msg = text_bytes[j*text_overflow+method:(j+1)*text_overflow+method]
                        msg = msg.decode('gbk')
                    party_tip += f"{msg}"
                    if j < text_newline-1:
                        party_tip += "\n"
        else :
            text_newline = 1
        total_text_line += text_newline
    #画图
        # 有特殊说明时金框提示
        rect_outline = ['GoldenRod',2] if info else [None,1]
        # 是补偿刀时红框提示
        if data[i]["remain"] !=0:
            rect_outline = ['DeepPink',2]
        # 当前行。文字行数超出最大值时进行处理，否则直到达到预定值才换列
        cur_row = count%colnum
        cur_col_px = total_text_line*text_size+cur_row*10+(cur_row+1)*(icon_size+10)
        if cur_col_px > col_overflow:
            add_count = colnum-count%colnum
            count += add_count
            cur_row = count%colnum
        if cur_row == 0 and i != 0:
            # x坐标换列
            posx = posx+icon_size*5+row_interval
            # 重置文字行溢出
            total_text_line = text_newline
        rect_position = [
            posx-5, 
            posy-5+cur_row*(icon_size+col_interval)+(total_text_line-text_newline)*text_size, 
            posx+5+icon_size*5, 
            posy+5+(cur_row+1)*icon_size+total_text_line*text_size+cur_row*col_interval
        ]
        if mode_tip:
            draw.rounded_rectangle(
                [rect_position[0],
                rect_position[1],
                rect_position[2],
                posy+5+(cur_row+1)*icon_size+(total_text_line-text_newline)*text_size+cur_row*col_interval],
                8,
                'DarkGray'
            )
            draw.multiline_text((
                    posx+1.25*icon_size,posy+cur_row*(icon_size+col_interval)+(total_text_line-text_newline+0.5)*text_size
                ), 
                '展示不下了！\n请访问 caimogu.cc/gzlj \n查看更多作业', 
                font=text_font, 
                fill="white",
                spacing=6,
                align='center'
            )
            break
        else:
            draw.rounded_rectangle(
                rect_position,
                8,
                'white',
                rect_outline[0],
                rect_outline[1]
            )
            units = [chara.fromid(i) for i in data[i]["unit"]]
            party_img = chara.gen_team_pic(units, icon_size, star_slot_verbose=False)
            base.paste(party_img,(
                    posx,posy+cur_row*(icon_size+col_interval)+total_text_line*text_size
                )
            )
            draw.multiline_text((
                    posx,posy-3+cur_row*(icon_size+col_interval)+(total_text_line-text_newline)*text_size
                ), 
                party_tip, 
                font=text_font, 
                fill="black",
                spacing=2
            )
        count += 1
    base.save(f'{PATH}/tmp/{date}_{boss_id}.jpg')
    return base