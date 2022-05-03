import time
import json
import os
from hoshino import Service,aiorequests
from .generate import *


sv = Service('公会战作业', enable_on_default=True, visible=True)

URL = "https://www.caimogu.cc/gzlj/data"
PATH = f'{os.path.dirname(os.path.abspath(__file__))}'
resource = {
    "last_req_time": None,
    "res":{}
}
stageid_dict = {
    "a":0,"A":0, "b":1,"B":1, "c":2,"C":2, "d":3,"D":3
}
default_date = time.strftime("%Y-%m",time.localtime())

headers = {
    'authority': 'www.caimogu.cc',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9,ja;q=0.8',
    'referer': 'https://www.caimogu.cc/gzlj',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

params = {
    'date': f'{default_date}',
}

def saveJson(res: json, date):
    with open(f'{PATH}/{date}.json', "w") as f:
        json.dump(res, f, indent=4)
      
def loadJson(date):
    global resource
    with open(f'{PATH}/{date}.json') as f:
        resource = json.load(f)

def takeDamageElement(elem):
    return elem["damage"]
      
async def parseHomework(res: json, boss_id):
    homeworks = res["data"][boss_id]["homework"]
    homework_num = len(homeworks)
    sv.logger.info(f"获取bossid{boss_id}的作业数量：{homework_num}")
    #对作业按伤害重新排序
    homeworks.sort(key=takeDamageElement, reverse=True)
    #只取auto作业
    auto_list = []
    for index in range(0,homework_num):
        tag = homeworks[index]["sn"]
        if "T" in tag or "W" in tag:
            # units = homeworks[index]["unit"]
            # units = [chara.fromid(i).name for i in units]
            # damage = homeworks[index]["damage"]
            # remain = homeworks[index]["remain"] if homeworks[index]["remain"] !=0 else ""
            # homework_str += f"{tag} {damage}万"
            # if remain !="":
                # homework_str += f"+{remain}秒"
            # homework_str += f"\n{units}\n"
            auto_list.append(homeworks[index])
        else:
            continue
    sv.logger.info(f"自动作业数量{len(auto_list)}")
    print(auto_list)
    base64_str = generateImg(auto_list)
    return base64_str
    
try:
    loadJson(default_date)
except:
    pass
    
@sv.on_prefix('查作业')
async def requestHomework(bot, ev):
    global resource
    #解析要查询的boss编号以及是否附带历史日期
    timestamp = int(time.time())
    arg = ev.message.extract_plain_text().split(" ")
    if not arg:
        await bot.finish(ev, "请附带要查询的阶段数和boss编号。\n例如：查作业 D5")
    if len(arg) > 2:
        await bot.finish(ev, "参数个数错误。\n正确输入格式为：查作业 boss编号 [日期]")
    else:
        if len(arg[0]) != 2:
            await bot.finish(ev, "boss编号不正确。\n正确输入例如：查作业 D5")
        try:
            stage_id = stageid_dict[arg[0][0]]
            boss_id = stage_id+(int(arg[0][1])-1)*4
        except Exception:
            await bot.finish(ev, "boss编号不正确。\n正确输入例如：查作业 D5")
        if len(arg) == 2:
            date = arg[1]
            print(date)
            try:
                loadJson(date)
                sv.logger.info('Loader:loaded history homework')
            except:
                #不存在该json，尝试下载
                params["date"]=date
                res = await aiorequests.get(URL, params=params, headers=headers)
                resource["last_req_time"] = timestamp
                resource["res"] = await res.json()
                saveJson(resource, date)
                #await bot.finish(ev, "日期格式不正确或不存在此日期作业，\n正确输入例如：查作业 D5 2022-04")
        else:
            date = default_date
            loadJson(date)
            sv.logger.info('Loader:loaded default homework')
    # 检查上次请求的时间,没超过15分钟就使用缓存
    if resource["last_req_time"] != None and timestamp-resource["last_req_time"] < 1800:
        sv.logger.info("FileMode:triggered using cached file")
        pass
    else:
        #超过15分钟 重新获取并保存
        sv.logger.info('FileMode:triggered requesting online homework')
        params["date"]=date
        res = await aiorequests.get(URL, params=params, headers=headers)
        resource["last_req_time"] = timestamp
        resource["res"] = await res.json()
        saveJson(resource, date)
    if resource["res"]["status"] == 0:
        await bot.finish(ev, "不存在本月数据。\n你可以输入“历史作业”查看以前的作业")
    base64_str = await parseHomework(resource["res"], boss_id)
    await bot.send(ev, f"[CQ:image,file={base64_str}]")