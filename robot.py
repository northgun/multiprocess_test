#!/usr/bin/env python
#-*- coding:utf-8 -*-

import socket,msgpack,json,time,random,sys,os,signal,redis,struct

import httpclient
import config

appid = 20001
time_gamestart = time.time()
number_find = 0
fightend_time = int(time.time())
found_need = 8
finish_signal = False
seat_id = 0
user_score = 0
flag = 0
r = redis.StrictRedis('localhost',6380)

#监控子进程是否关闭
def onsigchld(a,b): 
    global flag
    flag = 1     
signal.signal(signal.SIGCHLD,onsigchld) 

#连接socket
def connect():
    # get the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(config.SOCKET_SERVER);
    return sock
#登录
def login(sock, params):
    #login the server
    random_robot = random.randint(0,len(config.ROBOT_NAME))
    robot_name = config.ROBOT_NAME[random_robot].encode('utf-8')
    raw_msg ={"action": 'login',"ts": int(time.time()),"data":{"nickname":robot_name, "avatar":"http://gac.stg.haalee.com/static/img/rbhead/00"+str(random_robot)+".jpg", "match_id":params['match_id'], "rk_uid": params['rk_uid']}}
    struct_data = msg_pack(raw_msg, 0, 0, 0, 0)
    sock.send(struct_data);
    szBuf = sock.recv(1024);
    print szBuf

#发送请求
def msg_pack(message, proto_type, room_id, participant_ids, src_id):
    if proto_type ==0:
        msgpack_data = json.dumps(message, ensure_ascii=False)
    else:
        msgpack_data = message
    packdata_length = len(msgpack_data)
    pack_str = '>ihbbhHhBBBBB'+str(packdata_length)+'s'
    global appid
    struct_data = struct.pack(pack_str, packdata_length+19, appid, 0, proto_type, room_id, participant_ids, src_id,0,0,0,0,0, msgpack_data)
    return struct_data


#创建房间
def roomcreate(sock,params):
    match_id = params['match_id']
    rk_uid = params['rk_uid']
    access_token = params['access_token']
    ####
    #获取桌子匹配信息
    resp2 = httpclient.get_pair(rk_uid,params)
    seat_num = resp2['seat_num']
    battle_id = resp2['battle_id']
    f_uid = resp2['participant']['rk_uid']
    params['seat_num'] = seat_num
    params['battle_id'] = battle_id
    params['f_uid'] = f_uid
    params['round'] = resp2['round']
    params['step'] = resp2['step']
    params['inning'] = resp2['inning']
    raw_msg = {"action":"roomcreate","ts":1370677197749 ,"data":{'seat_num':seat_num, "match_id":match_id,"battle_id":battle_id}}
    print 'raw_msg',raw_msg
    struct_data = msg_pack(raw_msg, 0, 0, 0, 0)#msg_pack(raw_msg, 0)
    sock.send(struct_data)
    count = 0
    while True:
        response = sock.recv(1024)
        count +=1
        #print 'roomcreate response: ', response,type(response)
        #print '0',response,'1'
        try:
            result = json.loads(response[19:])
        except:
            break
        global seat_id
        try:
            if 'data' in result.keys() and len(result['data']['peers']) == 1:
                #print 'seat————id',result['data']['seat_id']
                seat_id = result['data']['seat_id']
                #print 'sssss',seat_id
            if 'data' in result.keys() and len(result['data']['peers']) == 2:
                if seat_id ==0:

                    if result['data']['joinpeers']['seat_id'] == 2:
                        seat_id = 1
                    else:
                        seat_id = 2
                break
        except:
            break
        #print 'count',count
        #if count ==2:
        #    break
        time.sleep(1)
    return params

#对战过程中监听对手分数
def fight_back(sock,params):
    count = 0
    rate = 0.5 #0.5去取一次返回
    while True:

        response = sock.recv(1024)
        r1 = response[19:]
        #硬编码，如果长度是fight接口数据传输的长度
        if len(r1) == 6:
            r2 = struct.unpack('<hhh',r1) 
            ##往存储里面放一个数据
            
            global r
            r.set('rs1'+str(params['robot_no']),r2[1])
            #如果对方找到8个了

            print 'fuckfuckfuckfuckfuckfuck', r2[0],r2[1]
        if len(r1) ==7:
            pid = os.getpid()
            os.kill(int(pid),signal.SIGUSR1)
        count +=1 
        time.sleep(rate)

#对战过程中给对手发分数
def fight(sock,params):
    score_count = 0
    time_count = 0
    c_time = 0
    pid = os.fork()
    if pid == 0:
        #开启一个监听的进程
        fight_back(sock,params)
    else:
        #获取对手等级
        opponent_info = httpclient.get_opponent_info(params)
        print opponent_info
        if opponent_info['ret'] == 0:
            opponent_level = str(opponent_info['userinfo']['game_level'])
        else:
            opponent_level = 1
        #机器人继续执行找东西的动作
        score,sl_time = get_pro(opponent_level)
        while True:
            
            global flag
            if flag:
                break
            
            c_time+=1
            if c_time >= sl_time:

                c_time = 0
                time_count += sl_time
                
                score_count += score
                ##往存储里面放一个数据
                global r
                r.set('rs0'+str(params['robot_no']),score_count)
                #######
                if score_count < 0:
                    score_count = 0

                if time_count>=60:
                    sl_time = sl_time - (time_count-60) +5

                global seat_id
                raw_msg = struct.pack('<hhh',100,9-score_count,0)   
                struct_data = msg_pack(raw_msg, 1, 0, 65535,seat_id)
                print 'ffffuuccckk',score_count,time_count
                sock.send(struct_data)
                if score_count >=9  or time_count>=60:
                    if score_count == 9:
                        raw_msg = struct.pack('<hhhb',101,1,0,0)
                    else:
                        raw_msg = struct.pack('<hhhb',101,0,0,0)
                    struct_data = msg_pack(raw_msg, 1, 0, 65535,seat_id)
                    sock.send(struct_data)
                    print '99999999999999999999999999999'
                    break;
                score,sl_time = get_pro(opponent_level)
            time.sleep(1)

#获取机器人的行为
def get_pro(opponent_level):
    score = 0
    sl_time = 10 #默认一个值，避免配置出错机器人异常生猛
    robot_level = get_robot_rate(opponent_level)
    ROBOT_LIST = config.PRO_NEW[robot_level]
    ROBOT_INFO = config.PRO_NEW[robot_level][random.randint(0,len(ROBOT_LIST)-1)]
    tmp = random.randint(1,100)
    if tmp < ROBOT_INFO['r']:
        score = 1
    else:
        score = 1
    sl_time = random.randint(ROBOT_INFO['t'][0],ROBOT_INFO['t'][1])
    return score,sl_time

#获取机器人的随机等级
def get_robot_rate(opponent_level):
    if int(opponent_level)>20:
        opponent_level = '20'
    RB_RATE = config.ROBOT_RATE[opponent_level]['rb_rate']
    tmp = 0
    count = 0
    rand = random.randint(1,100)
    for i in RB_RATE:
        tmp += i
        if rand <= tmp:
            return config.ROBOT_RATE[opponent_level]['rb_level'][count]
        count += 1



#机器人逻辑启动
def robot(params):
    print 'params',params
    sock = connect()
    login(sock,params)
    global appid 
    appid = int(params['appid'])
    #前端先等待7秒，让玩家好进来
    isGameOver = False 
    while True:
        
        if isGameOver:
            break
        params = roomcreate(sock,params)
        while True:
            global flag
            flag = 0
            time.sleep(5+3)
            #开始比赛
            print '))))))))))))))))',params['f_uid']
            if int(params['f_uid']) < 10000000:
                print '$$$$$$$$$$$$$$$$$$$$$$$$$'
                time.sleep(20)
            else:
                fight(sock,params)
            #提交成绩
            global r
            params['robot0_score'] = r.get('rs0'+str(params['robot_no']))
            params['robot1_score'] = r.get('rs1'+str(params['robot_no']))
            if not params['robot0_score']:
                params['robot0_score'] = random.randint(0,9)
            if not params['robot1_score']:
                params['robot1_score'] = random.randint(0,9)
            try:
                r.delete('rs0'+str(params['robot_no']))
                r.delete('rs1'+str(params['robot_no']))
            except:
                pass
            ret = httpclient.submit_score(params)
            if ret['ret'] == 0:
                params['round'] = ret['round']
                params['step'] = ret['step']
                params['inning'] = ret['inning']
            if ret['ret'] == 0 and ret['next_battle'] ==1:

                #还有下一局，继续fight
                continue

            elif ret['ret'] == 0 and ret['next_battle'] == 2:
                #循环去取轮结果
                isRoundOver = False
                while True:
                    
                    ret1 = httpclient.get_round_result(params)
                    if ret1['ret'] == 0:
                        if ret1['unfinish_battle_num'] == 0:
                            if ret1['promotion'] == True:
                                #可以进行下一轮
                                #先听x秒，这个数由数据中心决定
                                time.sleep(ret1['remain_time'])
                                isRoundOver = True
                                break
                            else:
                                isRoundOver = True
                                isGameOver = True
                                break
                        else:
                            #还得继续循环
                            time.sleep(2)
                            continue
                    else:
                        #报错了
                        isRoundOver = True
                        isGameOver = True
                        break
                if isRoundOver:
                    break
                
            else:
                isGameOver = True
                break        
    sock.close()

#测试用
if __name__ == "__main__":
    print 'sys.argv',sys.argv
    if len(sys.argv) < 2:
        exit()
    robot(sys.argv[1],sys.argv[2],sys.argv[3])


