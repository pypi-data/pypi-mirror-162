'''
测试BlfOb 读数据
'''

from BlfIoObjs import *
from BlfIo import BlfObjFromBytes, BlfIo
import random
import time
from multiprocessing import Process

import threading

def TestReadFile():
    blfio_ = BlfIo()
    res_ = blfio_.OpenReplayFile(r"Z:\log_1659518748.8437243.blf")
    counter_ = 0
    counter_tag_ = 10000
    counter_bash_ = 0
    if (res_ == 0):
        while(True):
            is_succ, time_, time_type, obj_ = blfio_.ReplayNext()
            if (is_succ != 0):
                break
            print('Time, {0}, obj, {1}'.format(time_, obj_.ToDict()))
            counter_ += 1
            if (counter_ % counter_tag_ == 0):
                counter_bash_ += 1
                print('读了 {0} 个 10000 条'.format(counter_bash_)) 
        blfio_.CloseReplyFile()

if __name__ == '__main__':
    task1_ = Process(target=TestReadFile, daemon=True)
    task2_ = Process(target=TestReadFile, daemon=True)
    task1_.start()
    # task2_.start()

    while (True):
        time.sleep(5)