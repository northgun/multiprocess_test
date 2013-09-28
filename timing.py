import time
import os
while True:
    time.sleep(60*30)
    os.popen('/bin/sh /data/sites/robot/robot_znm_normal/restart.sh').read()
    #break
