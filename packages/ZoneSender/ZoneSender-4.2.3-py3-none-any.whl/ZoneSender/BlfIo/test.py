import random
from BlfIoObjs import *
from BlfIo import BlfIo
import time


if __name__ == '__main__':
    blfio_ = BlfIo()
    # res_ = blfio_.OpenReplayFile('dae.blf')
    # print('OpenReplayFile ', res_)
    # res_ = 0
    # counter_ = 0
    # while (res_ == 0):
    #     res_, obj_ = blfio_.ReplayNext()
    #     counter_+=1
    #     # print('ReplayNext ', res_)
    #     # print(obj_.ToDict())
    # print('counter: ', counter_)
    # res_ = blfio_.CloseReplyFile()
    # print('CloseReplyFile ', res_)


    # res_ = blfio_.OpenLogFile('Z:/blf_io_log/blf_out_{0}.blf'.format(time.strftime('%M%S%H')))
    # print('OpenLogFile ', res_)
    # time_start_ = time.time()
    # for i_ in range(1000):
    #     data_ = [random.randint(0, 0xFF) for i_ in range(8)]
    #     # data_ = []
    #     blfio_.LogNext(CanFdMessage64Py(
    #         channel=3, 
    #         dlc=8, 
    #         id=0xFA, 
    #         data=data_, 
    #         dir=2))
    # res_ = blfio_.CloseLogFile()
    # print(time.time() - time_start_)
    # print('CloseLogFile ', res_)

    # 测试打开不存在的文件读取
    # blfio_.OpenReplayFile('dae.blf')
    # for i_ in range(100):
    #     res_, time_stamp_, time_stamp_type_, obj_ = blfio_.ReplayNext()
    #     print('--------------------------------------')
    #     print('res_ {0}'.format(res_))
    #     print('time_stamp_ {0}'.format(time_stamp_))
    #     print('time_stamp_type_ {0}'.format(time_stamp_type_))
    #     print('obj_ {0}'.format(obj_.ToDict()))

    # 测试写入文件
    res_ = blfio_.OpenLogFile('Z:/blf_io_log/blf_out_{0}.blf'.format(time.strftime('%M%S%H')))
    print('OpenLogFile ', res_)
    time_start_ = time.time()

    log_times_ = 10
    data_ = [0, 0xFF, 0x1F, 0x02, 0x56, 0xAC, 0xDE, 0x06]
    for j_ in range(10000):
        for i_ in range(log_times_):
            blfio_.LogNext(CanMessagePy(
                channel=i_,
                flags=0x01,
                dlc=8,
                id=i_,
                data=data_,
            ))
        for i_ in range(log_times_):
            blfio_.LogNext(CanMessage2Py(
                channel=i_,
                flags=0x00,
                dlc=8,
                id=i_,
                data=data_,
            ))
        for i_ in range(log_times_):
            blfio_.LogNext(CanFdMessagePy(
                channel=i_,
                flags=0x01,
                dlc=8,
                id=i_,
                data=data_,
            ))
        for i_ in range(log_times_):
            blfio_.LogNext(CanFdMessage64Py(
                channel=i_, 
                dlc=8, 
                id=i_, 
                data=data_
            ))
        for i_ in range(log_times_):
            blfio_.LogNext(LinMessagePy(
                channel=i_,
                id=i_,
                dlc=8,
                data=data_,
            ))
        for i_ in range(log_times_):
            blfio_.LogNext(LinMessage2Py(
                data=data_
            ))
        for i_ in range(log_times_):
            blfio_.LogNext(EthernetFramePy(
                sourceAddress=[0x02, 0x80, 0x5E, 0x1F, 0x01, 0x02],
                channel=i_,
                destinationAddress=[0x01, 0xFF, i_, 0x02, 0x34, 0x33],
                dir=0x01,
                type=i_,
                tpid=i_,
                tci=i_,
                payLoadLength=8,
                payLoad=data_,
            ))

    res_ = blfio_.CloseLogFile()
    print(time.time() - time_start_)
    print('CloseLogFile ', res_)
