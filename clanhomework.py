import time
import json
import os
from hoshino import Service,aiorequests
from hoshino.util import pic2b64
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
      
async def parseHomework(res: json, boss_id, date):
    homeworks = res["data"][boss_id]["homework"]
    homework_num = len(homeworks)
    sv.logger.info(f"获取bossid {boss_id} 的作业数量：{homework_num}")
    #对作业按伤害重新排序
    homeworks.sort(key=takeDamageElement, reverse=True)
    #只取auto作业
    auto_list = []
    for index in range(0,homework_num):
        tag = homeworks[index]["sn"]
        if ("T" in tag or "W" in tag):
            auto_list.append(homeworks[index])
        else:
            continue
    sv.logger.info(f"自动作业数量：{len(auto_list)}")
    im = generateImg(auto_list, boss_id, date)
    base64_str = pic2b64(im)
    return base64_str
    
async def downloadResource(date, timestamp):
    global resource
    params["date"]=date
    res = await aiorequests.get(URL, params=params, headers=headers)
    resource["last_req_time"] = timestamp
    resource["res"] = await res.json()
    saveJson(resource, date)
    
    
@sv.on_prefix('查作业')
async def requestHomework(bot, ev):
    global resource
    start_time = int(round((time.time()) * 1000))
    #解析要查询的boss编号以及是否附带历史日期
    timestamp = int(time.time())
    arg = ev.message.extract_plain_text().split(" ")
    if not arg:
        await bot.finish(ev, "请附带要查询的阶段数和boss编号。\n例如：查作业 D5 2022-04（日期可以省略）")
    if len(arg) > 2:
        await bot.finish(ev, "参数个数错误。\n正确输入格式为：查作业 boss编号 [日期]")
    else:
        if len(arg[0]) != 2:
            await bot.finish(ev, "boss编号不正确。\n正确boss编号格式为：阶段数+第几只。例如：查作业 D5")
        try:
            stage_id = stageid_dict[arg[0][0]]
            boss_id = stage_id+(int(arg[0][1])-1)*4
        except Exception:
            await bot.finish(ev, "boss编号不正确。\n正确boss编号格式为：阶段数+第几只。例如：查作业 D5")
        if len(arg) == 2:
            date = arg[1]
            try:
                loadJson(date)
                sv.logger.info('Loader:loaded history homework')
            except:
                #不存在该json，尝试下载
                await downloadResource(date, timestamp)
                sv.logger.info('Loader:loaded downloaded homework')
        else:
            date = default_date
            try:
                loadJson(default_date)
                sv.logger.info('Loader:loaded default homework')
            except:
                await downloadResource(date, timestamp)
                sv.logger.info('Loader:loaded downloaded homework')
    # 是否有作业
    if resource["res"]["status"] == 0:
        await bot.finish(ev, f'[CQ:image,file=file:///{PATH}/assests/error.png]', at_sender=True)
    # 检查上次请求的时间,没超过15分钟就使用缓存
    if resource["last_req_time"] != None and timestamp-resource["last_req_time"] < 900:
        tmp_fp = f'{PATH}/tmp/{date}_{boss_id}.jpg'
        if os.path.exists(tmp_fp):
            sv.logger.info("FileMode:using cached res&pic file")
            await bot.finish(ev, f'[CQ:image,file=file:///{PATH}/tmp/{date}_{boss_id}.jpg]', at_sender=True)
        else:
            sv.logger.info("FileMode:using cached res... generating pic file")
            base64_str = await parseHomework(resource["res"], boss_id, date)
    else:
        #超过15分钟 重新获取并保存
        sv.logger.info('FileMode:requesting online homework file')
        params["date"]=date
        res = await aiorequests.get(URL, params=params, headers=headers)
        resource["last_req_time"] = timestamp
        resource["res"] = await res.json()
        saveJson(resource, date)
        base64_str = await parseHomework(resource["res"], boss_id, date)
    end_time = int(round((time.time()) * 1000))
    await bot.send(ev, f"[CQ:image,file={base64_str}]", at_sender=True)
    sv.logger.info(f'Process succeed in {end_time-start_time}ms')