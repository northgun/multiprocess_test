ps aux | grep 'cheduler_znm_normal'| awk '{print $2}' | xargs kill -9
~
