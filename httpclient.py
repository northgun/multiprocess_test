#-*- coding: utf-8 -*-
import httplib
import simplejson as json
import urllib

API_HOST = "gac.rekoo.net"
APIVersion = 2
#验证用户是否有对战的权限

#发送http请求，method为保留字段
def http_send(method,get_data):
    conn = httplib.HTTPConnection(API_HOST)
    uri = '/api/?'
    uri += urllib.urlencode(get_data)
    print '++++++++++++++++++++++++++++++',uri
    conn.request('GET', uri)
    content = conn.getresponse()
    try:
        tent = content.read()
        tent = tent.replace('false','False').replace('true','True')
        print '------------------------------',tent
        result = eval(tent)
    except:
        result = {'ret':1}
    conn.close()
    return result

#获取机器人配置
def get_robot_config():
    method = 'vsapi.get_robot_config'
    get_data = {
        'method': method,
    }
    return http_send('GET',get_data)

#即时赛报名接口
def signup_normal_game(rk_uid,access_token,match_type):
    conn = httplib.HTTPConnection(API_HOST)
    #conn = httplib.HTTPConnection("www.python.org")
    uri = "/api/?competition_system_id="+match_type+"&access_token="+access_token+"&rk_uid="+rk_uid+"&method=match.sign_up"
    conn.request('GET', uri)
    #print uri
    #conn.request('GET', '/index.html')
    content = conn.getresponse()
    try:
        tent = content.read()
        #print 'tent',tent
        tent = tent.replace('false','False').replace('true','True')
        result = eval(tent)
    except:
        result = {'ret':-1}
    conn.close()
    return result

#获取即时赛需要人数
def get_sign_up_num(rk_uid,access_token,match_id):
    conn = httplib.HTTPConnection(API_HOST)
    #conn = httplib.HTTPConnection("www.python.org")
    uri = "/api/?access_token="+access_token+"&rk_uid="+rk_uid+"&method=match.get_sign_up_num&match_id="+match_id
    conn.request('GET', uri)
    #print uri
    #conn.request('GET', '/index.html')
    content = conn.getresponse()
    try:
        tent = content.read()
        #print 'tent',tent
        tent = tent.replace('false','False').replace('true','True')
        result = eval(tent)
    except:
        result = {'ret':-1}
    conn.close()
    return result



#获取匹配信息
def get_pair(rk_uid,params):
    method = 'match.get_pair'
    get_data = {
        'method': method,
        'access_token':params['access_token'],
        'rk_uid':params['rk_uid'],
        'match_id':params['match_id'],
        'APIVersion':APIVersion,
        'appid':str(params['appid']),
    }
    return http_send('GET',get_data)


#即时赛退出报名
def sign_out(rk_uid,access_token,match_id):
    conn = httplib.HTTPConnection(API_HOST)
    #conn = httplib.HTTPConnection("www.python.org")
    uri = "/api/?access_token="+access_token+"&rk_uid="+rk_uid+"&method=match.sign_out&match_id="+match_id
    conn.request('GET', uri)
    print uri
    #conn.request('GET', '/index.html')
    content = conn.getresponse()
    try:
        tent = content.read()
        print 'tent',tent
        tent = tent.replace('false','False').replace('true','True')
        result = eval(tent)
    except:
        result = {'ret':-1}
    conn.close()
    return result



#询问数据中心是否需要机器人
def get_instant_match_need_num(match_type,appid):
    method = 'vsapi.get_instant_match_need_num'
    get_data = {
        'method': method,
        'competition_system_id': match_type,

        'appid':appid,
    }
    return http_send('GET',get_data)

#用户登录
def loginauth(params):
    method = 'login.auth'
    get_data = {
        'method': method,
        'platform': 'robot',
        'robot_id': params['mac'],
        'appid':str(params['appid']),
    }
    return http_send('GET',get_data)

#获取对手信息
def get_opponent_info(params):
    method = 'vsapi.get_opponent_info'
    get_data = {
        'method': method,
        'f_uid': params['f_uid'],
        'appid':str(params['appid']),
    }
    return http_send('GET',get_data)

#提交局结果
def submit_score(params):
    method = 'match.submit_score'
    if params['robot0_score'] > params['robot1_score']:
        result0 = True
        result1 = False
    elif params['robot0_score'] < params['robot1_score']:
        result0 = True
        result1 = False
    else:
        result0 = False
        result1 = False
    battle_score = {'data':[
            #robot0_score是自己的分数，robot1_score是对手的分数
            {'rk_uid':params['rk_uid'],'find_num':params['robot0_score'],'time':50,'result':result0},
            {'rk_uid':params['f_uid'],'find_num':params['robot1_score'],'time':50,'result':result1},
        ]}
    get_data = {
        'method': method,
        'match_id': params['match_id'],
        'access_token': params['access_token'],
        'rk_uid': params['rk_uid'],
        'battle_id': params['battle_id'],
        'battle_score' : json.dumps(battle_score),
        'appid':str(params['appid']),
        'round':params['round'],
        'step':params['step'],
        'inning':params['inning'],
        'APIVersion':APIVersion,
    }

    return http_send('GET',get_data)

#检查用户状态，处理一场情况的
def check_user_match(params):
    method = 'match.check_user_match'
    get_data = {
        'method': method,
        'rk_uid': params['rk_uid'],
        'access_token': params['access_token'],
        'appid':str(params['appid']),
    }
    return http_send('GET',get_data)

#获取轮结果信息
def get_round_result(params):
    conn = httplib.HTTPConnection(API_HOST)
    method = 'match.get_round_result'
    get_data = {
        'method': method,
        'match_id': params['match_id'],
        'access_token': params['access_token'],
        'rk_uid': params['rk_uid'],
        'appid':str(params['appid']),
         }
    return http_send('GET',get_data)

def checkuser2():
    import httplib
    conn = httplib.HTTPConnection("www.python.org")
    conn.request("GET", "/index.html")
    r1 = conn.getresponse()
    print r1.status, r1.reason

def battleend(battleid):
    #conn = httplib.HTTPConnection("gac.dev3.haalee.com")
    #conn.request("GET", "/api/?method=match.battleend&battleid="+str(battleid))
    #r1 = conn.getresponse()
    print battleid
    return 0

#暂时好像没用
def signup(access_token):
    conn = httplib.HTTPConnection(API_HOST)
    #conn = httplib.HTTPConnection("www.python.org")
    uri = '/api/?method=match.sign_up&access_token='+access_token+'&match_id=10046|1&demand_type=1&appid='+APPID
    conn.request('GET', uri)
    content = conn.getresponse()
    print '$$$',uri
    try:
        tent = content.read()
        print '####'
        print tent
        result = eval(tent)
    except:
        result = {'ret':1}
    conn.close()
    return result

#暂时不用
def getmatchnum(uid):
    conn = httplib.HTTPConnection("gac.dev.haalee.com")
    #conn = httplib.HTTPConnection("www.python.org")
    uri = '/api/?method=vsapi.getmatchnum&rk_uid='+uid
    conn.request('GET', uri)
    print uri
    #conn.request('GET', '/index.html')
    content = conn.getresponse()
    try:
        result = eval(content.read()).get('match_num_all')
        print 'hahahahaha'
    except:
        result = 0
        print 'wawawawawa'
    print '000000000000000000000000',result
    conn.close()
    return result

#暂时不用
def checkuser(uid,match_id):
    conn = httplib.HTTPConnection("gac.dev.haalee.com")
    #conn = httplib.HTTPConnection("www.python.org")
    uri = '/api/?method=vsapi.checkuser&rk_uid='+uid+'&match_id='+match_id
    conn.request('GET', uri)
    print uri
    #conn.request('GET', '/index.html')
    content = conn.getresponse()
    print '777',content.read()
    try:
        result = eval(content.read())
    except:
        result = {'ret':1}
    print '000000000000000000000000',result
    conn.close()
    return result


if __name__ == "__main__":
        checkuser()
