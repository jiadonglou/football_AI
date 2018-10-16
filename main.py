
# coding: utf-8

# In[19]:


# Import necessary modules
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config
# In[47]:


import requests
import json
#from google.cloud import translate
import os
import random
import urllib.request
import urllib.parse
import hashlib 
import datetime
import timedelta
import wave
import base64
from pydub import AudioSegment
from wxpy import *

# Create a trainer that uses this config
trainer = Trainer(config.load("./data/config_spacy.yml"))

# Load the training data
training_data = load_data('./data/football-rasa-chinese.json')

# Create an interpreter by training the model
interpreter = trainer.train(training_data)




# You choice of translator: google, youdao, or baidu
translator = 'baidu'

# Google Translate Credential Json File
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./data/Football-a337503a7b32.json"

# Youdao translate credential
appKey = '4cfb5abb68739eb9'
secretKey = 'ARngTMxyOUUnCxCmoxMvpTaRizDnbIAU'

# Baidu translate credential
appid = '20181012000218537'
sKey = 'OGVItM3RHXKGeUOUJHb2'

# betsAPI token
token = '13455-2ebneo03H11ZTs'

majorLeague = ['eu','kp','kr','us','cn','br','fr','es','gb','jp']
leagueDict = {'欧洲': 'eu','朝鲜': 'kp','韩国': 'kr','美国': 'us','中国': 'cn','法国': 'fr','巴西': 'br','西班牙': 'es','英国': 'gb',"日本": 'jp'} 

# Responses Template
responses = [
    '我需要更多信息！ 请告诉我这场比赛的{}？',
    "我找到这场比赛了，请问需要什么数据？", 
    "不好意思，我没办法找到您要的比赛信息。请重新输入要求。",
    '{} \n主队{} 客队{} \n比分为{}-{} 现在{}分钟',
    "本场{}的比赛在{}{}的{}举办,可容纳{}人",
    "主队阵容:{}\n客队阵容：{}",
    "角球 {}:{}\n黄牌 {}:{}\n红牌 {}:{}\n点球 {}:{}\n替换 {}:{}\n进攻 {}:{}\n危险进攻 {}:{}\n射正 {}:{}\n射偏 {}:{}\n控球率 {}%:{}%",
    '1.说\'你好\'来启动搜寻功能\n2.说\'再见\'来结束搜寻功能\n3.告诉我足球比赛的主队，客队，及日期信息来查询比赛。我可以帮你查询比赛实时比分，数据，阵容，场馆，以及事件。\n4.我也可以帮你查询正在进行中的比赛，并且根据你喜欢的国家来过滤比赛信息'                       
]


# In[48]:


def translate(source, fromLang, toLang):
    if translator == 'youdao':
        return youdao_translate(source, fromLang, toLang)
    if translator == 'google':
        return google_translate(source, fromLang, toLang)
    if translator == 'baidu':
        return baidu_translate(source, fromLang, toLang)
    
def youdao_translate(source, fromLang, toLang):
    url = 'http://openapi.youdao.com/api'
    salt = random.randint(1, 65536)
    q= source
    sign = appKey+q+str(salt)+secretKey
    sign = sign.encode('utf-8')
    m1 = hashlib.md5()
    m1.update(sign)
    sign = m1.hexdigest()
    
    dict = {'english' : 'EN', 'chinese' : 'zh-CHS'}
    fromLang = dict[fromLang]
    toLang = dict[toLang]
    
    data = {'from': fromLang, 'to': toLang, 'q':q,'doctype': 'json', 'appKey': appKey,'salt':salt,'sign':sign}

    data = urllib.parse.urlencode(data).encode('utf-8')
    wy = urllib.request.urlopen(url, data)
    html = wy.read().decode('utf-8')
    result = json.loads(html)
    return result['translation'][0]

def baidu_translate(source, fromLang, toLang):
    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    salt = random.randint(1, 65536)
    q= source
    sign = appid+q+str(salt)+sKey
    sign = sign.encode('utf-8')
    m1 = hashlib.md5()
    m1.update(sign)
    sign = m1.hexdigest()
    
    dict = {'english' : 'en', 'chinese' : 'zh'}
    fromLang = dict[fromLang]
    toLang = dict[toLang]
    data = {'from': fromLang, 'to': toLang, 'q':q,'doctype': 'json', 'appid': appid,'salt':salt,'sign':sign}

    data = urllib.parse.urlencode(data).encode('utf-8')
    wy = urllib.request.urlopen(url, data)
    html = wy.read().decode('utf-8')
    result = json.loads(html)
    return result['trans_result'][0]['dst']
            
def google_translate(source, fromLang, toLang):
    dict = {'english' : 'en', 'chinese' : 'zh_cn'}
    fromLang = dict[fromLang]
    toLang = dict[toLang]
    translate_client = translate.Client()
    translation = translate_client.translate(source, target_language=toLang)
    return translation['translatedText']

def youdao_voice_translate(source, fromLang, sample_rate, nchannels):
    url = 'http://openapi.youdao.com/asrapi'
    salt = random.randint(1, 65536)
    q= source
    sign = appKey+q.decode('utf-8')+str(salt)+secretKey
    sign = sign.encode('utf-8')
    m1 = hashlib.md5()
    m1.update(sign)
    sign = m1.hexdigest()
    
    dict = {'english' : 'EN', 'chinese' : 'zh-CHS'}
    fromLang = dict[fromLang]
    
    data = {'langType': fromLang, 'q':q,'doctype': 'json', 'appKey': appKey,'salt':salt,'sign':sign, 'format': 'wav', 'rate': sample_rate, 'channel':nchannels, 'type':1}

    data = urllib.parse.urlencode(data).encode('utf-8')
    wy = urllib.request.urlopen(url, data)
    html = wy.read().decode('utf-8')
    result = json.loads(html)
    print("语音识别：" + result['result'][0])
    return result['result'][0]
    

def read_params():
    with open('./temp/params.json') as json_file:
        params = json.load(json_file)
        return params

def write_params(params):
    with open('./temp/params.json','w') as outfile:
        json.dump(params,outfile)

def translate_params(params):
    now_time = datetime.datetime.now()
    params['home'] = translate(params['home'],'chinese','english')
    params['away'] = translate(params['away'],'chinese','english')
    d = params['date']
    if not d.isdigit():
        if d in ['今天','现在','马上','刚刚']:
            d = datetime.datetime.now().strftime('%Y%m%d')
        if d == '明天':
            edit_day=datetime.datetime.now()+datetime.timedelta(days=1)
            d = edit_day.strftime('%Y%m%d')
        if d == '后天':
            edit_day=datetime.datetime.now()+datetime.timedelta(days=2)
            d = edit_day.strftime('%Y%m%d')
        if d == '大后天':
            edit_day=datetime.datetime.now()+datetime.timedelta(days=3)
            d = edit_day.strftime('%Y%m%d')
        if d == '昨天':
            edit_day=datetime.datetime.now()-datetime.timedelta(days=1)
            d = edit_day.strftime('%Y%m%d')
        if d == '前天':
            edit_day=datetime.datetime.now()-datetime.timedelta(days=2)
            d = edit_day.strftime('%Y%m%d')
        if d == '大前天':
            edit_day=datetime.datetime.now()-datetime.timedelta(days=3)
            d = edit_day.strftime('%Y%m%d')
    params['date'] = d
    return params

def event_search(sport_id, home, away, time):
    search_url = "https://api.betsapi.com/v1/events/search?token={}"
    search_url = search_url.format(token)
    params = {
        'sport_id': sport_id,
        'home':home,
        'away':away,
        'time':time
    }
    return requests.get(search_url,params = params).json()  

def event_lineup(event_id):
    search_url = "https://api.betsapi.com/v1/event/lineup?token={}"
    search_url = search_url.format(token)
    params = {
        'event_id': event_id
    }
    return requests.get(search_url,params = params).json() 

def line_up(line_up_results):
    home_str = ""
    away_str = ""
    home = line_up_results["results"]["home"]["startinglineup"]
    away = line_up_results["results"]["away"]["startinglineup"]
    for i in home:
        home_str = home_str + i["shirtnumber"] + "号" + translate(i["player"]["name"],'english','chinese')+","
    for j in home:
        away_str = away_str + i["shirtnumber"] + "号" +translate(j["player"]["name"],'english','chinese')+","

    home_str = home_str[:-1]
    away_str = away_str[:-1]
    return responses[5].format(home_str, away_str)

def event_view(event_id):
    search_url = "https://api.betsapi.com/v1/event/view?token={}"
    search_url = search_url.format(token)
    params = {
        'event_id': event_id
    }
    return requests.get(search_url,params = params).json() 

def event_stats(event_view_results):
    s = event_view_results["results"][0]["stats"]
    return responses[6].format(s["corners"][0],s["corners"][1],s["yellowcards"][0],s["yellowcards"][1],s["redcards"][0],s["redcards"][1],s["penalties"][0],s["penalties"][1],s["substitutions"][0],s["substitutions"][1],s["attacks"][0],s["attacks"][1],s["dangerous_attacks"][0],s["dangerous_attacks"][1],s["on_target"][0],s["on_target"][1],s["off_target"][0],s["off_target"][1],s["possession_rt"][0],s["possession_rt"][1])
    
def event_events(event_view_results):
    output = "-----------------"
    e = event_view_results["results"][0]["events"]
    for i in e:
        output = output + "\n" + translate(i["text"],'english','chinese')
    return output

def inplay_event():
    search_url = "https://api.betsapi.com/v1/events/inplay?&token={}"
    search_url = search_url.format(token)
    params = {
        'sport_id' : 1
    }
    return requests.get(search_url,params = params).json() 



def voice_message():
    filename = './temp/msg.wav'
    extension = filename[filename.rindex('.')+1:]
    if extension == "wav" :
        # load wav
        file_to_play = wave.open(filename, 'rb')
        file_wav = open(r'./temp/msg.wav', 'rb')
        q = base64.b64encode(file_wav.read())
        file_wav.close()
        sample_rate = file_to_play.getframerate()
        nchannels = file_to_play.getnchannels()
        output_str = youdao_voice_translate(q,'chinese',sample_rate,nchannels)
        return output_str.replace('。', '')
        


# In[49]:


def search_respond(message, params):
    entities = interpreter.parse(message)["entities"]
    # Fill the dictionary with entities
    for ent in entities:
        params[ent["entity"]] = str(ent["value"])  

    # Check if necessary information is provided
    info = ""
    if 'home' not in params:
        if 'away' in params:
            del params['away']
        info = info + "主客队，"
    if 'away' not in params:
        if 'home' in params:
            del params['home']
        info = info + "主客队"
    if 'date' not in params:
        info = info + "日期,"
    info = info[:-1]
    # Prompt to request information
    if info != "":
        return responses[0].format(info), params
    
    params = translate_params(params) # Translate params from Chinese to English
    # Request Json file with match stats
    results = event_search(1, params['home'], params['away'],params['date'])
    params['event_id'] = results["results"][0]["id"]
    
    # If result not found, clear params and return error message
    if results['success'] == 0 or results['results'] == []:
        params = {"searching" : True}
        return responses[2], params
    
    else:
        if 'data' not in params:
            return responses[1], params
        else:
            data_type = params["data"]
            time_str = ""
            if results["results"][0]["time_status"] == "3": 
                time_str = "全场" + results["results"][0]["extra"]["length"]  
            if results["results"][0]["time_status"] == "1":
                time_str = "正在比赛"+ str(results["results"][0]["timer"]["tm"])
            if data_type == "分数" or data_type == "比分":
                return responses[3].format(translate(results["results"][0]["league"]["name"],'english','chinese'),translate(results["results"][0]["home"]["name"],'english','chinese'),translate(results["results"][0]["away"]["name"],'english','chinese'),results["results"][0]["scores"]["2"]["home"],results["results"][0]["scores"]["2"]["away"], time_str),params
            if data_type == '场馆':
                stadium = results["results"][0]["extra"]["stadium_data"]
                return responses[4].format(translate(results["results"][0]["league"]["name"],'english','chinese'),translate(stadium["country"],'english','chinese'),translate(stadium["city"],'english','chinese'),translate(stadium["name"],'english','chinese'),stadium["capacity"]), params
            if data_type == '阵容':
                line_up_results =  event_lineup(params['event_id'])
                return line_up(line_up_results),params
            if data_type == '数据':
                event_view_results = event_view(params['event_id'])
                return event_stats(event_view_results), params
            if data_type == '事件':
                event_view_results = event_view(params['event_id'])
                return event_events(event_view_results), params
            else:
                return responses[1], params
                


# In[54]:


def inplay_respond(message, params):
    entities = interpreter.parse(message)["entities"]
    # Fill the dictionary with entities
    for ent in entities:
        params[ent["entity"]] = str(ent["value"])  
    
    inplay_str = "进行中的比赛："
    results = inplay_event()
    if len(results['results']) == 0:
        return "没有进行中的比赛"
    n = results['pager']['total']
    #n = min(15, results['pager']['total']) 
    if "league" not in params:
        j = 0
        for i in range(n):
            if results['results'][i]['league']['cc'] in majorLeague: 
                if j < 10:  
                    inplay_str = inplay_str + "\n" + str(results['results'][i]['timer']['tm']) + "\' " + translate(results['results'][i]['league']['name'],'english','chinese') + " \n      " + translate(results['results'][i]['home']['name'],'english','chinese') + " " + str(results['results'][i]['scores']['2']['home']) + "-" + str(results['results'][i]['scores']['2']['away']) + " " + translate(results['results'][i]['away']['name'],'english','chinese')                       
                    j = j + 1
        if j < 10:
            for i in range(n):
                if results['results'][i]['league']['cc'] not in majorLeague: 
                    if j < 10:
                        inplay_str = inplay_str + "\n" + str(results['results'][i]['timer']['tm']) + "\' " + translate(results['results'][i]['league']['name'],'english','chinese') + " \n      " + translate(results['results'][i]['home']['name'],'english','chinese') + " " + str(results['results'][i]['scores']['2']['home']) + "-" + str(results['results'][i]['scores']['2']['away']) + " " + translate(results['results'][i]['away']['name'],'english','chinese')                       
                        j = j + 1               
    else:
        for i in range(n):
            cc = leagueDict[params["league"]]
            if results['results'][i]['league']['cc'] == cc: 
                inplay_str = inplay_str + "\n" + str(results['results'][i]['timer']['tm']) + "\' " + translate(results['results'][i]['league']['name'],'english','chinese') + " \n      " + translate(results['results'][i]['home']['name'],'english','chinese') + " " + str(results['results'][i]['scores']['2']['home']) + "-" + str(results['results'][i]['scores']['2']['away']) + " " + translate(results['results'][i]['away']['name'],'english','chinese')                       
    if 'league' in params:
        del params['league']    
    if inplay_str == "进行中的比赛：":
        inplay_str = "当前无进行中的比赛"
        
    return inplay_str, params
    
    


# In[55]:


def respond(message, params):
    intent = interpreter.parse(message)["intent"]['name']
    confidence = interpreter.parse(message)["intent"]['confidence']
    print(interpreter.parse(message)["intent"])
    if confidence < 0.45:
        return '', params
    if intent == 'help':
        return responses[7], params
    if intent == 'greet':
        params['searching'] = True
        return '你好～开启搜索模式',params
    if params['searching'] == False:
        return '', params
    if intent == 'goodbye' :
        params = {"searching" : False}
        return '再见～搜索模式关闭',params
    if intent == 'event_search' :
        return search_respond(message, params)
    if intent == 'inplay_event':
        return inplay_respond(message, params)
    else:
        return search_respond(message, params)
    


# In[56]:


def trans_mp3_to_wav(filepath):
    song = AudioSegment.from_mp3(filepath)
    low_sample_rate = song.set_frame_rate(16000)
    low_sample_rate.export("./temp/msg.wav", format="wav",bitrate="16k")


# In[58]:


db = {}
write_params(db)
bot = Bot()


#my_friend = bot.friends().search(u'JAYDEN')[0]

@bot.register()
def reply_friend(msg):
    db = read_params()
    response = ""
    if msg.type == 'Recording':
        if msg.sender.remark_name not in db:
            db[msg.sender.remark_name] = {"searching" : False} 
        print("来自" + msg.sender.remark_name + "的语音消息：")
        msg.get_file("./temp/msg.mp3")
        trans_mp3_to_wav("./temp/msg.mp3")
        response, params = respond(str(voice_message()), db[msg.sender.remark_name])
        db[msg.sender.remark_name] = params
        
    if msg.type == 'Text':
        if msg.sender.remark_name not in db:
            db[msg.sender.remark_name] = {"searching" : False}           
        print("来自" + msg.sender.remark_name + "的文字消息：" + str(msg.text))
        input = str(msg.text)
        response, params = respond(input, db[msg.sender.remark_name])
        db[msg.sender.remark_name] = params

        

    write_params(db)
    print("Replied: " + response)
    msg.reply(response)

# 堵塞线程，并进入 Python 命令行
embed()
