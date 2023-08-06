# array_ = bytearray()
# data_ = 0xFFFFFFFFFFFFFFF0
# bytes_ = data_.to_bytes(8, 'big', signed=False)
# array_.extend(bytes_)
# print(bytes_)

import os
import typing
import random
import time
import json
import csv

from multiprocessing import RLock, Process, Lock

from SharedMemZoneSender import SharedMemZoneSender

def BuildRandomData():
    d_ = {}
    l_ = []
    for i_ in range(10000):
        time_ = i_
        data_ = [random.randint(0, 0xFF)] * 1
        l_.append({
            'time': time_,
            'data': data_,
        })
    d_['data'] = l_

    file_name_ = 'random_data_' + time.strftime('%H%M%S') + '.json'
    with open(file_name_, mode='w+') as f_:
        f_.write(json.dumps(d_, indent=2))

def GetData() -> typing.List[dict]:
    # file_ = open('random_data_104015.json', mode='r')    # 10000
    file_ = open('random_data_103822.json', mode='r')    # 100
    d_ = json.loads(file_.read())
    return d_['data']

def ManagerFunction(rlock):
    shared_ = SharedMemZoneSender(rlock, create=True)
    while (True):
        time.sleep(5)

def ProviderFunction(rlock):
    shared_ = SharedMemZoneSender(rlock)
    data_ = GetData()
    print('Process:{0} 开始写入时间 {1}'.format(os.getpid(), time.time()))
    for i_ in data_:
        time_stamp_ns_ = i_['time']
        # print(time_stamp_ns_)
        data_ = i_['data']
        shared_.WriteNext(time_stamp_ns_, bytes(data_))
        time.sleep(0.001)
    print('Process:{0} 结束写入时间 {1}'.format(os.getpid(), time.time()))

def ProviderFunction2(rlock):
    shared_ = SharedMemZoneSender(rlock)
    # data_ = GetData()
    print('Process:{0} 开始写入时间 {1}'.format(os.getpid(), time.time()))
    # for i_ in range(10000):
    while (True):
        time_stamp_ns_ = time.time_ns()
        # print(time_stamp_ns_)
        # data_ = bytes([random.randint(0, 0xFF)] * 512)
        # data_ = bytes([1, 3, 0, 0, 0, 0])
        data_ = bytes([0, 0, 0])
        shared_.WriteNext(time_stamp_ns_, bytes(data_))
        time.sleep(0.001)
    print('Process:{0} 结束写入时间 {1}'.format(os.getpid(), time.time()))


def ConsumerFunction(rlock, name:int):
    shared_ = SharedMemZoneSender(rlock)
    # time.sleep(10)
    print('开始读数据 ConsumerFunction >>>>>')
    with open('Consumer_{0}.csv'.format(name), 'w', newline='') as f:
        writer = csv.writer(f)
        total_counter_ = 0
        while(True):
            time_stamp_ns_, data_ = shared_.ReadNext()
            if (len(data_) != 0):
                # total_counter_ += 1
                # print('写入, {0}, {1}'.format(time_stamp_ns_, list(data_)))
                writer.writerow((time_stamp_ns_, list(data_)))
                # print('已写入, {0}'.format(total_counter_))

def ConsumerFunction2(rlock, name:int):
    shared_ = SharedMemZoneSender(rlock)
    # time.sleep(10)
    print('开始读数据 ConsumerFunction2 >>>>>')
    with open('Consumer_{0}.csv'.format(name), 'w', newline='') as f:
        writer = csv.writer(f)
        total_counter_ = 0
        while(True):
            time.sleep(0.02)    # 100ms 读一次
            bytes_list_ = shared_.ReadToLatest()
            if (len(bytes_list_) != 0):
                # print(len(bytes_list_))
                total_counter_ += len(bytes_list_)
                writer.writerows(bytes_list_)
                print('Process, {0}, 已写入, {1}'.format(name, total_counter_))
        
def TestCsv():
    with open('some.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        while(True):
            # time_stamp_ns_, data_ = shared_.ReadNext()
            writer.writerow([time.time_ns(), bytes([0, 1, 2,6, 4])])
            time.sleep(0.1)

# def 

def TestMutilProcessIO():
    rlock_ = Lock()

    manager_process_ = Process(target=ManagerFunction, args=[rlock_], daemon=True)

    provider_process_1_ = Process(target=ProviderFunction2, args=[rlock_], daemon=True)
    provider_process_2_ = Process(target=ProviderFunction2, args=[rlock_], daemon=True)
    provider_process_3_ = Process(target=ProviderFunction2, args=[rlock_], daemon=True)
    provider_process_4_ = Process(target=ProviderFunction2, args=[rlock_], daemon=True)
    provider_process_5_ = Process(target=ProviderFunction2, args=[rlock_], daemon=True)
    provider_process_6_ = Process(target=ProviderFunction2, args=[rlock_], daemon=True)

    consumer_process_1_ = Process(target=ConsumerFunction2, args=[rlock_, 1], daemon=True)
    consumer_process_2_ = Process(target=ConsumerFunction2, args=[rlock_, 2], daemon=True)
    consumer_process_3_ = Process(target=ConsumerFunction2, args=[rlock_, 3], daemon=True)
    consumer_process_4_ = Process(target=ConsumerFunction2, args=[rlock_, 4], daemon=True)
    consumer_process_5_ = Process(target=ConsumerFunction2, args=[rlock_, 5], daemon=True)
    consumer_process_6_ = Process(target=ConsumerFunction2, args=[rlock_, 6], daemon=True)

    manager_process_.start()

    time.sleep(1)
    provider_process_1_.start()
    # provider_process_2_.start()
    # provider_process_3_.start()
    # provider_process_4_.start()
    # provider_process_5_.start()
    # provider_process_6_.start()

    time.sleep(1)
    consumer_process_1_.start()
    # consumer_process_2_.start()
    # consumer_process_3_.start()
    # consumer_process_4_.start()
    # consumer_process_5_.start()
    # consumer_process_6_.start()

    while(True):
        time.sleep(5)

def LockAcq(lock, name:int):
    # while(True)
    mem_ = SharedMemZoneSender(lock)
    print('进程 {0} 准备拿锁'.format(name))
    mem_.rlock.acquire(True)
    print('进程 {0} 拿到锁'.format(name))
    time.sleep(10)
    mem_.rlock.release()
    print('进程 {0} 释放锁'.format(name))

# def LockAcq2(lock):
#     mem_ = SharedListZoneSender(lock)
#     print('进程 2 准备拿锁')
#     mem_.rlock.acquire(True)
#     print('进程 2 拿到锁')
#     time.sleep(10)
#     mem_.rlock.release()
#     print('进程 2 释放锁')

def TestLock():
    rlock_ = Lock()

    manager_process_ = Process(target=ManagerFunction, args=[rlock_], daemon=True)

    provider_process_1_ = Process(target=LockAcq, args=[rlock_, 1], daemon=True)
    provider_process_2_ = Process(target=LockAcq, args=[rlock_, 2], daemon=True)
    provider_process_3_ = Process(target=LockAcq, args=[rlock_, 3], daemon=True)

    manager_process_.start()
    time.sleep(1)

    provider_process_1_.start()
    time.sleep(1)
    provider_process_2_.start()
    time.sleep(1)
    provider_process_3_.start()

    while(True):
        time.sleep(5)

if __name__ == '__main__':
    # BuildRandomData()

    TestMutilProcessIO()

    # TestLock()