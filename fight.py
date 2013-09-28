# -*- coding:utf-8 -*-
from multiprocessing import Process
import redis, time, os, random,sys
import robot
import multiprocessing
import config
import httpclient

#机器人运行
def robot_run(params):
    robot.robot(params)
    sys.exit(0)

#数据中心逻辑，是否派出机器人
def fight(num,match_type,appid):
    #num机器人编号
    mac = str(num)

    params = {}
    params['appid'] = appid
    #报名去
    #获取token
    params['mac'] = mac
    userinfo = httpclient.loginauth(params)
    if userinfo['ret'] == 0:
        rk_uid = userinfo['rk_uid']
        access_token = userinfo['access_token']
        params['rk_uid'] = rk_uid
        params['access_token'] = access_token

        #丹华说调着玩的一个api
        #httpclient.check_user_match(params)

        #获取match_id
        resp = httpclient.signup_normal_game(rk_uid,access_token,match_type)
        if resp['ret'] == 12023:
            match_id = resp['match_id']
            signout = httpclient.sign_out(rk_uid,access_token,match_id)
            resp = httpclient.signup_normal_game(rk_uid,access_token,match_type)
        if resp['ret'] == 0:
            match_id = resp['match_id']
            while True:

                #获取用户的是否满了
                resp1 = httpclient.get_sign_up_num(rk_uid,access_token,match_id)
                if resp1['ret'] == 0 and resp1['started'] == True:
                    break
                time.sleep(2)
            params['robot_no'] = num
            params['match_id'] = match_id
            robot_run(params)
            #有了分桌信息，那就开打了～

if __name__ == '__main__':
    fight(sys.argv[1],sys.argv[2],sys.argv[3])
    