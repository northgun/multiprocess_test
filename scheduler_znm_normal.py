# -*- coding:utf-8 -*-
import time, os, random,sys
import fight
import httpclient

def robot_run(num,match_type,appid):
    fight.fight(num,match_type,appid)
    sys.exit(0)

if __name__ == '__main__':
    #赛制类型
    match_type = sys.argv[1]
    #机器人开始的数目
    rb_start_num = num = int(sys.argv[2])
    #机器人结束的个数
    rb_end_num = int(sys.argv[3])
    appid = sys.argv[4]
    while True:
        time.sleep(random.randint(5,5))
        resp = httpclient.get_instant_match_need_num(match_type,appid)
        print '//////////////////////////////////////////////////////',num
        if resp['ret'] == 0 :
            if resp['need_num'] >0:
                #分配机器人 
                ret = os.fork()
                if ret == 0:
                    robot_run(num,match_type,appid)
                num+=1
                if num>rb_end_num:
                    num = rb_start_num






        


