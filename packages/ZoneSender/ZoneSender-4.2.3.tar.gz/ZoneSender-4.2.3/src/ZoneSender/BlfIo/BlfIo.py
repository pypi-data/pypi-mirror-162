import copy
import ctypes
import random
import typing
import time
from pathlib import Path

from .BlfIoObjs import *


def BlfObjFromBytes(data:bytes) -> BlfIoStruct:
    # a_= data[0]
    obj_type_ = data[0]
    d_ = json.loads(data[1:].decode('utf-8'))
    try:
        del d_['_blfObjType']
    except:
        pass
    
    if (obj_type_ == BLF_ObjectType.CAN_FD_MESSAGE):
        return CanFdMessagePy(**d_)
    elif (obj_type_ == BLF_ObjectType.CAN_FD_MESSAGE_64):
        return CanFdMessage64Py(**d_)
    elif (obj_type_ == BLF_ObjectType.CAN_MESSAGE):
        return CanMessagePy(**d_)
    elif (obj_type_ == BLF_ObjectType.CAN_MESSAGE2):
        return CanMessage2Py(**d_)
    elif (obj_type_ == BLF_ObjectType.LIN_MESSAGE):
        return LinMessagePy(**d_)
    elif (obj_type_ == BLF_ObjectType.LIN_MESSAGE2):
        return LinMessage2Py(**d_)
    elif (obj_type_ == BLF_ObjectType.ETHERNET_FRAME):
        return EthernetFramePy(**d_)
    else:
        return BlfIoStruct()


class BlfIo(object):
    def __init__(self, dll_path: str = '') -> None:
        '''
        blfIO 操作库
        :param dll_path:str dll 的路径，默认为本文件通路径下的 blf_io_export.dll
        '''
        if (dll_path == ''):
            # 如果是默认的 dll 路径
            dll_path = str(Path(__file__).absolute().parent / 'blf_io_export.dll')
        # print(dll_path)
        
        
        # 类内变量 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self._log_start_ns = 0


        # Dll Obj >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self._dll_blf_io_export = ctypes.cdll.LoadLibrary(dll_path)


        # Dll Function >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self._dllFuncOpenReplayFile = self._dll_blf_io_export.OpenReplayFile
        self._dllFuncOpenReplayFile.argtypes = [ctypes.c_char_p]
        self._dllFuncOpenReplayFile.restype = ctypes.c_int

        self._dllFuncCloseReplayFile = self._dll_blf_io_export.CloseReplayFile
        self._dllFuncCloseReplayFile.restype = ctypes.c_int

        self._dllFuncReplayNext = self._dll_blf_io_export.ReplayNext
        # p_header_type, p_obj_type, p_time_stamp, p_time_stamp_type
        self._dllFuncReplayNext.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
        self._dllFuncReplayNext.restype = ctypes.c_int

        self._dllFuncOpenLogFile = self._dll_blf_io_export.OpenLogFile
        self._dllFuncOpenLogFile.argtypes = [ctypes.c_char_p]
        self._dllFuncOpenLogFile.restype = ctypes.c_int

        self._dllFuncCloseLogFile = self._dll_blf_io_export.CloseLogFile
        self._dllFuncCloseLogFile.restype = ctypes.c_int

        self._dllFuncLogNext = self._dll_blf_io_export.LogNext
        self._dllFuncLogNext.argtypes = [ctypes.c_uint32, ctypes.c_uint64]
        self._dllFuncLogNext.restype = ctypes.c_int
        

        # Dll Variable >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Header 结构体 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.OBJECT_HEADER_PY_REPLAY = ctypes.POINTER(ObjectHeaderPy)
        self.P_OBJECT_HEADER_PY_REPLAY = self.OBJECT_HEADER_PY_REPLAY.in_dll(self._dll_blf_io_export, 'P_OBJECT_HEADER_PY_REPLAY')
        self.OBJECT_HEADER_2_PY_REPLAY = ctypes.POINTER(ObjectHeader2Py)
        self.P_OBJECT_HEADER_2_PY_REPLAY = self.OBJECT_HEADER_2_PY_REPLAY.in_dll(self._dll_blf_io_export, 'P_OBJECT_HEADER_2_PY_REPLAY')

        # Replay 相关结构体 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.CAN_FD_MESSAGE_PY_REPLAY = ctypes.POINTER(CanFdMessagePy)
        self.P_CAN_FD_MESSAGE_PY_REPLAY = self.CAN_FD_MESSAGE_PY_REPLAY.in_dll(self._dll_blf_io_export, 'P_CAN_FD_MESSAGE_PY_REPLAY')
        self.CAN_FD_MESSAGE_64_PY_REPLAY = ctypes.POINTER(CanFdMessage64Py)
        self.P_CAN_FD_MESSAGE_64_PY_REPLAY = self.CAN_FD_MESSAGE_64_PY_REPLAY.in_dll(self._dll_blf_io_export, 'P_CAN_FD_MESSAGE_64_PY_REPLAY')
        self.CAN_MESSAGE_PY_REPLAY = ctypes.POINTER(CanMessagePy)
        self.P_CAN_MESSAGE_PY_REPLAY = self.CAN_MESSAGE_PY_REPLAY.in_dll(self._dll_blf_io_export, 'P_CAN_MESSAGE_PY_REPLAY')
        self.CAN_MESSAGE_2_PY_REPLAY = ctypes.POINTER(CanMessage2Py)
        self.P_CAN_MESSAGE_2_PY_REPLAY = self.CAN_MESSAGE_2_PY_REPLAY.in_dll(self._dll_blf_io_export, 'P_CAN_MESSAGE_2_PY_REPLAY')
        self.LIN_MESSAGE_PY_REPLAY = ctypes.POINTER(LinMessagePy)
        self.P_LIN_MESSAGE_PY_REPLAY = self.LIN_MESSAGE_PY_REPLAY.in_dll(self._dll_blf_io_export, 'P_LIN_MESSAGE_PY_REPLAY')
        self.LIN_MESSAGE_2_PY_REPLAY = ctypes.POINTER(LinMessage2Py)
        self.P_LIN_MESSAGE_2_PY_REPLAY = self.LIN_MESSAGE_2_PY_REPLAY.in_dll(self._dll_blf_io_export, 'P_LIN_MESSAGE_2_PY_REPLAY')
        self.ETHERNET_FRAME_PY_REPLAY = ctypes.POINTER(EthernetFramePy)
        self.P_ETHERNET_FRAME_PY_REPLAY = self.ETHERNET_FRAME_PY_REPLAY.in_dll(self._dll_blf_io_export, 'P_ETHERNET_FRAME_PY_REPLAY')

        # Log 相关结构体 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.CAN_FD_MESSAGE_PY_LOG = ctypes.POINTER(CanFdMessagePy)
        self.P_CAN_FD_MESSAGE_PY_LOG = self.CAN_FD_MESSAGE_PY_LOG.in_dll(self._dll_blf_io_export, 'P_CAN_FD_MESSAGE_PY_LOG')
        self.CAN_FD_MESSAGE_64_PY_LOG = ctypes.POINTER(CanFdMessage64Py)
        self.P_CAN_FD_MESSAGE_64_PY_LOG = self.CAN_FD_MESSAGE_64_PY_LOG.in_dll(self._dll_blf_io_export, 'P_CAN_FD_MESSAGE_64_PY_LOG')
        self.CAN_MESSAGE_PY_LOG = ctypes.POINTER(CanMessagePy)
        self.P_CAN_MESSAGE_PY_LOG = self.CAN_MESSAGE_PY_LOG.in_dll(self._dll_blf_io_export, 'P_CAN_MESSAGE_PY_LOG')
        self.CAN_MESSAGE_PY_2_LOG = ctypes.POINTER(CanMessage2Py)
        self.P_CAN_MESSAGE_2_PY_LOG = self.CAN_MESSAGE_PY_2_LOG.in_dll(self._dll_blf_io_export, 'P_CAN_MESSAGE_2_PY_LOG')
        self.LIN_MESSAGE_PY_LOG = ctypes.POINTER(LinMessagePy)
        self.P_LIN_MESSAGE_PY_LOG = self.LIN_MESSAGE_PY_LOG.in_dll(self._dll_blf_io_export, 'P_LIN_MESSAGE_PY_LOG')
        self.LIN_MESSAGE_PY_2_LOG = ctypes.POINTER(LinMessage2Py)
        self.P_LIN_MESSAGE_2_PY_LOG = self.LIN_MESSAGE_PY_2_LOG.in_dll(self._dll_blf_io_export, 'P_LIN_MESSAGE_2_PY_LOG')
        self.ETHERNET_FRAME_PY_LOG = ctypes.POINTER(EthernetFramePy)
        self.P_ETHERNET_FRAME_PY_LOG = self.ETHERNET_FRAME_PY_LOG.in_dll(self._dll_blf_io_export, 'P_ETHERNET_FRAME_PY_LOG')
    

    def OpenReplayFile(self, path: str) -> int:
        '''
        打开一个回放文件
        :param path: str 回放文件的路径
        :return: int
            - 0: 打开成功
            - 1: 打开失败 
            - 2: 文件不存在
        '''
        if (not Path(path).is_file()):
            return 1
        if (not Path(path).exists()):
            return 2
        res_ = self._dllFuncOpenReplayFile(path.encode('utf-8'))
        # print(type(res_))
        return res_

    def CloseReplyFile(self) -> int:
        '''
        关闭当前回放的文件
        :return: int\n
            - 0: 关闭成功\n
            - 1: 没有打开的回放文件
        '''
        return self._dllFuncCloseReplayFile()

    def ReplayNext(self) -> typing.Tuple[int, int, int, BlfIoStruct]:
        '''
        回放下一个报文
        :return:[0]int 是否读取成功
            - 0: 读取成功
            - 1: 文件损坏
            - 2: 下一条报文损坏
            - 3: 下一条报文是空指针
            - 4: 没有打开的文件
        :return:[1]int 时间戳
        :return:[2]int 时间戳类型
            - 0: 未知
            - 1: ms
            - 2: ns
        :return:[3]BlfIoStruct 下一个数据，可能为如下类型
            - CanFdMessagePy
            - CanFdMessage64Py
            - CanMessagePy
            - Canmessage2Py
            - LinMessagePy
            - LinMessage2Py
            - EthernetFramePy
        '''
        header_type_ = ctypes.c_uint32()    # 头类型
        obj_type_ = ctypes.c_uint32()    # 对象类型
        time_stamp_ = 0    # 时间戳数据
        time_stamp_type_ = 0    # 时间戳类型
        obj_ = BlfIoStruct()    # 返回的数据对象
        
        res_ = self._dllFuncReplayNext(ctypes.pointer(header_type_), ctypes.pointer(obj_type_))
        
        if (not (res_ == 0)):
            # 读取失败
            return res_, 0, 0, BlfIoStruct()

        # 检查 object_type
        # print('header_type = {0}'.format(header_type_.value))
        if (header_type_.value == 1):
            # ObjectHeader
            time_stamp_ = self.P_OBJECT_HEADER_PY_REPLAY.contents.objectTimeStamp
            time_stamp_type_ = self.P_OBJECT_HEADER_PY_REPLAY.contents.objectFlags
        elif (header_type_.value == 2):
            # ObjectHeader2
            time_stamp_ = self.P_OBJECT_HEADER_2_PY_REPLAY.contents.objectTimeStamp
            time_stamp_type_ = self.P_OBJECT_HEADER_2_PY_REPLAY.contents.objectFlags

        if (obj_type_.value == BLF_ObjectType.CAN_FD_MESSAGE):
            # obj_ = copy.deepcopy(self.P_CAN_FD_MESSAGE_PY_REPLAY.contents)
            obj_ = self.P_CAN_FD_MESSAGE_PY_REPLAY.contents
            obj_._blfObjType = BLF_ObjectType.CAN_FD_MESSAGE

        if (obj_type_.value == BLF_ObjectType.CAN_FD_MESSAGE_64):
            # obj_ = copy.deepcopy(self.P_CAN_FD_MESSAGE_64_PY_REPLAY.contents)
            obj_ = self.P_CAN_FD_MESSAGE_64_PY_REPLAY.contents
            obj_._blfObjType = BLF_ObjectType.CAN_FD_MESSAGE_64

        if (obj_type_.value == BLF_ObjectType.CAN_MESSAGE):
            # obj_ = copy.deepcopy(self.P_CAN_MESSAGE_PY_REPLAY.contents)
            obj_ = self.P_CAN_MESSAGE_PY_REPLAY.contents
            obj_._blfObjType = BLF_ObjectType.CAN_MESSAGE

        if (obj_type_.value == BLF_ObjectType.CAN_MESSAGE2):
            # obj_ = copy.deepcopy(self.P_CAN_MESSAGE_2_PY_REPLAY.contents)
            obj_ = self.P_CAN_MESSAGE_2_PY_REPLAY.contents
            obj_._blfObjType = BLF_ObjectType.CAN_MESSAGE2

        if (obj_type_.value == BLF_ObjectType.LIN_MESSAGE):
            # obj_ = copy.deepcopy(self.P_LIN_MESSAGE_PY_REPLAY.contents)
            obj_ = self.P_LIN_MESSAGE_PY_REPLAY.contents
            obj_._blfObjType = BLF_ObjectType.LIN_MESSAGE

        if (obj_type_.value == BLF_ObjectType.LIN_MESSAGE2):
            # obj_ = copy.deepcopy(self.P_LIN_MESSAGE_2_PY_REPLAY.contents)
            obj_ = self.P_LIN_MESSAGE_2_PY_REPLAY.contents
            obj_._blfObjType = BLF_ObjectType.LIN_MESSAGE2

        if (obj_type_.value == BLF_ObjectType.ETHERNET_FRAME):
            # obj_ = copy.deepcopy(self.P_ETHERNET_FRAME_PY_REPLAY.contents)
            obj_ = self.P_ETHERNET_FRAME_PY_REPLAY.contents
            obj_._blfObjType = BLF_ObjectType.ETHERNET_FRAME
            
        return res_, time_stamp_, time_stamp_type_, obj_

    def OpenLogFile(self, path: str) -> int:
        '''
        创建一个记录文件
        :param path: str 回放文件的路径
        :return: int\n
            - 0: 打开成功\n
            - 1: 已经有打开的文件了\n
            - 2: 打开文件失败 
        '''
        res_ = self._dllFuncOpenLogFile(path.encode('utf-8'))
        # print(type(res_))
        if (res_ == 0):
            self._log_start_ns = time.time_ns()
        return res_

    def CloseLogFile(self) -> int:
        '''
        关闭当前的记录文件
        :return: int\n
            - 0: 关闭成功\n
            - 1: 没有打开的回放文件
        '''
        return self._dllFuncCloseLogFile()

    def LogNext(self,obj: 'BlfIoStruct', time_stamp_ns: int = -1) -> int:
        '''
        记录一个 Frame
        :return: int\n
            - 0: 记录成功\n
            - 1: 文件未打开\n
            - 10: 未知的数据结构
        '''
        time_stamp_ns_ = time_stamp_ns
        if (time_stamp_ns_ < 0):
            time_stamp_ns_ = time.time_ns() - self._log_start_ns
        else:
            time_stamp_ns = time_stamp_ns >> 16
        if (isinstance(obj, CanFdMessagePy)):
            self.P_CAN_FD_MESSAGE_PY_LOG.contents = obj
            return self._dllFuncLogNext(ctypes.c_uint32(BLF_ObjectType.CAN_FD_MESSAGE), ctypes.c_uint64(time_stamp_ns_))
        if (isinstance(obj, CanFdMessage64Py)):
            self.P_CAN_FD_MESSAGE_64_PY_LOG.contents = obj
            return self._dllFuncLogNext(ctypes.c_uint32(BLF_ObjectType.CAN_FD_MESSAGE_64), ctypes.c_uint64(time_stamp_ns_))
        if (isinstance(obj, CanMessagePy)):
            self.P_CAN_MESSAGE_PY_LOG.contents = obj
            return self._dllFuncLogNext(ctypes.c_uint32(BLF_ObjectType.CAN_MESSAGE), ctypes.c_uint64(time_stamp_ns_))
        if (isinstance(obj, CanMessage2Py)):
            self.P_CAN_MESSAGE_2_PY_LOG.contents = obj
            return self._dllFuncLogNext(ctypes.c_uint32(BLF_ObjectType.CAN_MESSAGE2), ctypes.c_uint64(time_stamp_ns_))
        if (isinstance(obj, LinMessagePy)):
            self.P_LIN_MESSAGE_PY_LOG.contents = obj
            return self._dllFuncLogNext(ctypes.c_uint32(BLF_ObjectType.LIN_MESSAGE), ctypes.c_uint64(time_stamp_ns_))
        if (isinstance(obj, LinMessage2Py)):
            self.P_LIN_MESSAGE_2_PY_LOG.contents = obj
            return self._dllFuncLogNext(ctypes.c_uint32(BLF_ObjectType.LIN_MESSAGE2), ctypes.c_uint64(time_stamp_ns_))
        if (isinstance(obj, EthernetFramePy)):
            self.P_ETHERNET_FRAME_PY_LOG.contents = obj
            return self._dllFuncLogNext(ctypes.c_uint32(BLF_ObjectType.ETHERNET_FRAME), ctypes.c_uint64(time_stamp_ns_))
        return 10
