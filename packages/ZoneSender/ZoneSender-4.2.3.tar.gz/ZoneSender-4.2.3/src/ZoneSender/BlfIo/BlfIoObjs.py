import ctypes
import typing
import json


class BLF_ObjectType(object):
    UNKNOWN = 0 # /**< unknown object */
    CAN_MESSAGE = 1 # /**< CAN message object */
    CAN_ERROR = 2 # /**< CAN error frame object */
    CAN_OVERLOAD = 3 # /**< CAN overload frame object */
    CAN_STATISTIC = 4 # /**< CAN driver statistics object */
    APP_TRIGGER = 5 # /**< application trigger object */
    ENV_INTEGER = 6 # /**< environment integer object */
    ENV_DOUBLE = 7 # /**< environment double object */
    ENV_STRING = 8 # /**< environment string object */
    ENV_DATA = 9 # /**< environment data object */
    LOG_CONTAINER = 10 # /**< container object */
    LIN_MESSAGE = 11 # /**< LIN message object */
    LIN_CRC_ERROR = 12 # /**< LIN CRC error object */
    LIN_DLC_INFO = 13 # /**< LIN DLC info object */
    LIN_RCV_ERROR = 14 # /**< LIN receive error object */
    LIN_SND_ERROR = 15 # /**< LIN send error object */
    LIN_SLV_TIMEOUT = 16 # /**< LIN slave timeout object */
    LIN_SCHED_MODCH = 17 # /**< LIN scheduler mode change object */
    LIN_SYN_ERROR = 18 # /**< LIN sync error object */
    LIN_BAUDRATE = 19 # /**< LIN baudrate event object */
    LIN_SLEEP = 20 # /**< LIN sleep mode event object */
    LIN_WAKEUP = 21 # /**< LIN wakeup event object */
    MOST_SPY = 22 # /**< MOST spy message object */
    MOST_CTRL = 23 # /**< MOST control message object */
    MOST_LIGHTLOCK = 24 # /**< MOST light lock object */
    MOST_STATISTIC = 25 # /**< MOST statistic object */
    Reserved26 = 26 # /**< reserved */
    Reserved27 = 27 # /**< reserved */
    Reserved28 = 28 # /**< reserved */
    FLEXRAY_DATA = 29 # /**< FLEXRAY data object */
    FLEXRAY_SYNC = 30 # /**< FLEXRAY sync object */
    CAN_DRIVER_ERROR = 31 # /**< CAN driver error object */
    MOST_PKT = 32 # /**< MOST Packet */
    MOST_PKT2 = 33 # /**< MOST Packet including original timestamp */
    MOST_HWMODE = 34 # /**< MOST hardware mode event */
    MOST_REG = 35 # /**< MOST register data (various chips) */
    MOST_GENREG = 36 # /**< MOST register data (MOST register) */
    MOST_NETSTATE = 37 # /**< MOST NetState event */
    MOST_DATALOST = 38 # /**< MOST data lost */
    MOST_TRIGGER = 39 # /**< MOST trigger */
    FLEXRAY_CYCLE = 40 # /**< FLEXRAY V6 start cycle object */
    FLEXRAY_MESSAGE = 41 # /**< FLEXRAY V6 message object */
    LIN_CHECKSUM_INFO = 42 # /**< LIN checksum info event object */
    LIN_SPIKE_EVENT = 43 # /**< LIN spike event object */
    CAN_DRIVER_SYNC = 44 # /**< CAN driver hardware sync */
    FLEXRAY_STATUS = 45 # /**< FLEXRAY status event object */
    GPS_EVENT = 46 # /**< GPS event object */
    FR_ERROR = 47 # /**< FLEXRAY error event object */
    FR_STATUS = 48 # /**< FLEXRAY status event object */
    FR_STARTCYCLE = 49 # /**< FLEXRAY start cycle event object */
    FR_RCVMESSAGE = 50 # /**< FLEXRAY receive message event object */
    REALTIMECLOCK = 51 # /**< Realtime clock object */
    Reserved52 = 52 # /**< this object ID is available for the future */
    Reserved53 = 53 # /**< this object ID is available for the future */
    LIN_STATISTIC = 54 # /**< LIN statistic event object */
    J1708_MESSAGE = 55 # /**< J1708 message object */
    J1708_VIRTUAL_MSG = 56 # /**< J1708 message object with more than 21 data bytes */
    LIN_MESSAGE2 = 57 # /**< LIN frame object - extended */
    LIN_SND_ERROR2 = 58 # /**< LIN transmission error object - extended */
    LIN_SYN_ERROR2 = 59 # /**< LIN sync error object - extended */
    LIN_CRC_ERROR2 = 60 # /**< LIN checksum error object - extended */
    LIN_RCV_ERROR2 = 61 # /**< LIN receive error object */
    LIN_WAKEUP2 = 62 # /**< LIN wakeup event object  - extended */
    LIN_SPIKE_EVENT2 = 63 # /**< LIN spike event object - extended */
    LIN_LONG_DOM_SIG = 64 # /**< LIN long dominant signal object */
    APP_TEXT = 65 # /**< text object */
    FR_RCVMESSAGE_EX = 66 # /**< FLEXRAY receive message ex event object */
    MOST_STATISTICEX = 67 # /**< MOST extended statistic event */
    MOST_TXLIGHT = 68 # /**< MOST TxLight event */
    MOST_ALLOCTAB = 69 # /**< MOST Allocation table event */
    MOST_STRESS = 70 # /**< MOST Stress event */
    ETHERNET_FRAME = 71 # /**< Ethernet frame object */
    SYS_VARIABLE = 72 # /**< system variable object */
    CAN_ERROR_EXT = 73 # /**< CAN error frame object (extended) */
    CAN_DRIVER_ERROR_EXT = 74 # /**< CAN driver error object (extended) */
    LIN_LONG_DOM_SIG2 = 75 # /**< LIN long dominant signal object - extended */
    MOST_150_MESSAGE = 76 # /**< MOST150 Control channel message */
    MOST_150_PKT = 77 # /**< MOST150 Asynchronous channel message */
    MOST_ETHERNET_PKT = 78 # /**< MOST Ethernet channel message */
    MOST_150_MESSAGE_FRAGMENT = 79 # /**< Partial transmitted MOST50/150 Control channel message */
    MOST_150_PKT_FRAGMENT = 80 # /**< Partial transmitted MOST50/150 data packet on asynchronous channel */
    MOST_ETHERNET_PKT_FRAGMENT = 81 # /**< Partial transmitted MOST Ethernet packet on asynchronous channel */
    MOST_SYSTEM_EVENT = 82 # /**< Event for various system states on MOST */
    MOST_150_ALLOCTAB = 83 # /**< MOST50/150 Allocation table event */
    MOST_50_MESSAGE = 84 # /**< MOST50 Control channel message */
    MOST_50_PKT = 85 # /**< MOST50 Asynchronous channel message */
    CAN_MESSAGE2 = 86 # /**< CAN message object - extended */
    LIN_UNEXPECTED_WAKEUP = 87,
    LIN_SHORT_OR_SLOW_RESPONSE = 88,
    LIN_DISTURBANCE_EVENT = 89,
    SERIAL_EVENT = 90,
    OVERRUN_ERROR = 91 # /**< driver overrun event */
    EVENT_COMMENT = 92,
    WLAN_FRAME = 93,
    WLAN_STATISTIC = 94,
    MOST_ECL = 95 # /**< MOST Electrical Control Line event */
    GLOBAL_MARKER = 96,
    AFDX_FRAME = 97,
    AFDX_STATISTIC = 98,
    KLINE_STATUSEVENT = 99 # /**< E.g. wake-up pattern */
    CAN_FD_MESSAGE = 100 # /**< CAN FD message object */
    CAN_FD_MESSAGE_64 = 101 # /**< CAN FD message object */
    ETHERNET_RX_ERROR = 102 # /**< Ethernet RX error object */
    ETHERNET_STATUS = 103 # /**< Ethernet status object */
    CAN_FD_ERROR_64 = 104 # /**< CAN FD Error Frame object */
    LIN_SHORT_OR_SLOW_RESPONSE2 = 105,
    AFDX_STATUS = 106 # /**< AFDX status object */
    AFDX_BUS_STATISTIC = 107 # /**< AFDX line-dependent busstatistic object */
    Reserved108 = 108,
    AFDX_ERROR_EVENT = 109 # /**< AFDX asynchronous error event */
    A429_ERROR = 110 # /**< A429 error object */
    A429_STATUS = 111 # /**< A429 status object */
    A429_BUS_STATISTIC = 112 # /**< A429 busstatistic object */
    A429_MESSAGE = 113 # /**< A429 Message */
    ETHERNET_STATISTIC = 114 # /**< Ethernet statistic object */
    Unknown115 = 115,
    Reserved116 = 116,
    Reserved117 = 117,
    TEST_STRUCTURE = 118 # /**< Event for test execution flow */
    DIAG_REQUEST_INTERPRETATION = 119 # /**< Event for correct interpretation of diagnostic requests */
    ETHERNET_FRAME_EX = 120 # /**< Ethernet packet extended object */
    ETHERNET_FRAME_FORWARDED = 121 # /**< Ethernet packet forwarded object */
    ETHERNET_ERROR_EX = 122 # /**< Ethernet error extended object */
    ETHERNET_ERROR_FORWARDED = 123 # /**< Ethernet error forwarded object */
    FUNCTION_BUS = 124 # /**< FunctionBus object */
    DATA_LOST_BEGIN = 125 # /**< Data lost begin */
    DATA_LOST_END = 126 # /**< Data lost end */
    WATER_MARK_EVENT = 127 # /**< Watermark event */
    TRIGGER_CONDITION = 128 # /**< Trigger Condition event */
    CAN_SETTING_CHANGED = 129 # /**< CAN Settings Changed object */
    DISTRIBUTED_OBJECT_MEMBER = 130 # /**< Distributed object member (communication setup) */
    ATTRIBUTE_EVENT = 131 # /**< ATTRIBUTE event (communication setup) */

class BlfIoStruct(ctypes.Structure):
    def __init__(self) -> None:
        super().__init__()
        self._blfObjType = BLF_ObjectType.UNKNOWN

    def ToDict(self) -> dict:
        '''
        转换成 字典，也是转换为 bytes 的其中一步
        '''
        return {
            '_blfObjType':self._blfObjType
        }

    def ToBytes(self) -> bytes:
        '''
        序列化为 bytes
        '''
        # a_ = self._blfObjType.to_bytes(length=1, byteorder='big', signed=False)
        return self._blfObjType.to_bytes(length=1, byteorder='big', signed=False) + bytes(json.dumps(self.ToDict()), encoding='utf-8')
        # return bytes(json.dumps(self.ToDict()), encoding='utf-8')

class ObjectHeaderPy(BlfIoStruct):
    _fields_ = [
        ('signature', ctypes.c_uint32),
        ("headerSize", ctypes.c_uint16),
        ("headerVersion", ctypes.c_uint16),
        ("objectSize", ctypes.c_uint32),
        ("objectType", ctypes.c_uint32),
        ("objectFlags", ctypes.c_uint32),
        ("clientIndex", ctypes.c_uint16),
        ("objectVersion", ctypes.c_uint16),
        ("objectTimeStamp", ctypes.c_uint64),
        ]

class ObjectHeader2Py(BlfIoStruct):
    _fields_ = [
        ('signature', ctypes.c_uint32),
        ("headerSize", ctypes.c_uint16),
        ("headerVersion", ctypes.c_uint16),
        ("objectSize", ctypes.c_uint32),
        ("objectType", ctypes.c_uint32),
        ("objectFlags", ctypes.c_uint32),
        ("timeStampStatus", ctypes.c_uint8),
        ("reservedObjectHeader", ctypes.c_uint8),
        ("objectVersion", ctypes.c_uint16),
        ("objectTimeStamp", ctypes.c_uint64),
        ("originalTimeStamp", ctypes.c_uint64),
        ]

class CanFdMessagePy(BlfIoStruct):
    _fields_ =[
        ('channel', ctypes.c_uint8),
        ('flags', ctypes.c_uint8),
        ('dlc', ctypes.c_uint8),
        ('id', ctypes.c_uint32),
        ('frameLength', ctypes.c_uint32),
        ('arbBitCount', ctypes.c_uint8),
        ('canFdFlags', ctypes.c_uint8),
        ('validDataBytes', ctypes.c_uint8),
        ('reservedCanFdMessage1', ctypes.c_uint8),
        ('reservedCanFdMessage2', ctypes.c_uint32),
        ('data', ctypes.c_int8*64),
        ('reservedCanFdMessage3', ctypes.c_uint32),
        ('_dataLength', ctypes.c_uint16),
    ]
    def __init__(
        self,
        channel:int=0,
        flags:int=0x1000,
        dlc:int=0,
        id:int=0,
        frameLength:int=0,
        arbBitCount:int=0,
        canFdFlags:int=0x01,
        validDataBytes:int=0,
        reservedCanFdMessage1:int=0,
        reservedCanFdMessage2:int=0,
        data:typing.List[int]=[],
        reservedCanFdMessage3:int=0) -> None:
        '''
        CanFdMessage Object
        :param channel:int 通道
        :param flags:int flags
            - Bit0:TX
            - Bit5:NERR
            - Bit6:WU
            - Bit7:RTR
        :param dlc:int dlc
        :param id:int id
        :param frameLength:int 报文长度 非必须
        :param arbBitCount:int 仲裁场的数据长度 非必须
        :param canFdFlags:int canFdFlags 非必须
            - Bit0:EDL
            - Bit1:BRS
            - Bit2:ESI
        :param validDataBytes:int 有效的数据场长度 非必须
        :param reservedCanFdMessage1:int 保留 非必须
        :param reservedCanFdMessage2:int 保留 非必须
        :param data:list[int] 数据场 需要和 dlc 匹配
        :param reservedCanFdMessage3:int 保留
        '''
        super().__init__()
        self.channel = channel
        self.flags = flags
        self.dlc = dlc
        self.id = id
        self.frameLength = frameLength
        self.arbBitCount = arbBitCount
        self.canFdFlags = canFdFlags
        self.validDataBytes = validDataBytes
        self.reservedCanFdMessage1 = reservedCanFdMessage1
        self.reservedCanFdMessage2 = reservedCanFdMessage2
        self.reservedCanFdMessage3 = reservedCanFdMessage3
        self._dataLength = len(data)
        self.data = (ctypes.c_int8*64)(*data)
        self._blfObjType = BLF_ObjectType.CAN_FD_MESSAGE

    def ToDict(self) -> dict:
        d_ = super().ToDict()
        d_.update({
            'channel': self.channel,
            'flags': self.flags,
            'dlc': self.dlc,
            'id': self.id,
            'frameLength': self.frameLength,
            'arbBitCount': self.arbBitCount,
            'canFdFlags': self.canFdFlags,
            'validDataBytes': self.validDataBytes,
            'reservedCanFdMessage1': self.reservedCanFdMessage1,
            'reservedCanFdMessage2': self.reservedCanFdMessage2,
            'reservedCanFdMessage3': self.reservedCanFdMessage3,
            'data': list(ctypes.string_at(self.data, self._dataLength)),
        })
        return d_



    # def ToBytes(self) -> bytes:
    #     header_ =  super().ToBytes()
    #     return header_ \
    #         + self._dataLength.to_bytes(2, byteorder='big', signed=False) \
    #         + self.channel.to_bytes(1, byteorder='big', signed=False) \
    #         + self.flags.to_bytes(1, byteorder='big', signed=False) \
    #         + self.dlc.to_bytes(1, byteorder='big', signed=False) \
    #         + self.id.to_bytes(4, byteorder='big', signed=False) \
    #         + self.frameLength.to_bytes(4, byteorder='big', signed=False) \
    #         + self.arbBitCount.to_bytes(1, byteorder='big', signed=False) \
    #         + self.canFdFlags.to_bytes(1, byteorder='big', signed=False) \
    #         + self.validDataBytes.to_bytes(1, byteorder='big', signed=False) \
    #         + self.reservedCanFdMessage1.to_bytes(1, byteorder='big', signed=False) \
    #         + self.reservedCanFdMessage2.to_bytes(4, byteorder='big', signed=False) \
    #         + bytes(list(ctypes.string_at(self.data, self._dataLength))) \
    #         + self.reservedCanFdMessage3.to_bytes(4, byteorder='big', signed=False) \

class CanFdMessage64Py(BlfIoStruct):
    _fields_ =[
        ('channel', ctypes.c_uint8),
        ('dlc', ctypes.c_uint8),
        ('validDataBytes', ctypes.c_uint8),
        ('txCount', ctypes.c_uint8),
        ('id', ctypes.c_uint32),
        ('frameLength', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('btrCfgArb', ctypes.c_uint32),
        ('btrCfgData', ctypes.c_uint32),
        ('timeOffsetBrsNs', ctypes.c_uint32),
        ('timeOffsetCrcDelNs', ctypes.c_uint32),
        ('dir', ctypes.c_uint8),
        ('extDataOffset', ctypes.c_uint8),
        ('crc', ctypes.c_uint32),
        ('data', ctypes.c_uint8*64),
        ('_dataLength', ctypes.c_uint16),
    ]
    def __init__(
        self, 
        channel: int = 0, 
        dlc: int = 0, 
        validDataBytes: int = 0, 
        txCount: int=0, 
        id: int=0, 
        frameLength: int = 0, 
        flags: int=0x1000,
        btrCfgArb: int=0,
        btrCfgData: int=0,
        timeOffsetBrsNs: int=0,
        timeOffsetCrcDelNs: int=0,
        dir:int=0,
        extDataOffset: int=0,
        crc: int=0,
        data: list = []) -> None:
        '''
        CanFdMessage64 Object
        :param channel:int 通道
        :param dlc:int dlc
        :param validDataBytes:int 有效的数据场长度 非必须
        :param txCount:int txQuiredCount 和 txReqCount
            - Bits(0-3):required tranmission 数量
            - Bits(4-7):transmission attempts 的最大数量
        :param id:int id
        :param frameLength:int 报文长度 非必须
        :param flags:int flags
            - Bit0:0x0001 一定是 0
            - Bit1:0x0002 保留
            - Bit2:0x0004 1=NERR
            - Bit3:0x0008 1=High voltage 唤醒
            - Bit4:0x0010 1=远程帧
            - Bit5:0x0020 保留为0
            - Bit6:0x0040 1=Tx Ack
            - Bit7:0x0080 1=Tx Request
            - Bit8:0x0100 保留
            - Bit9:0x0200 SRR(CANFD)
            - Bit10:0x0400 R0
            - Bit11:0x0800 R1
            - Bit12:0x1000 EDL
            - Bit13:0x2000 BRS(CANFD)
            - Bit14:0x4000 ESI
            - Bit15:0x8000 保留
            - Bit16:0x10000 保留
            - Bit17:0x20000 1=Frame 是 burst 的一部分
            - Bit18-31:保留
        :param btrCfgArb:int 仲裁场的配置 非必须
            - Bit0-7:晶振频率
            - Bit8-15:预分频系数
            - Bit16-23:BTL Cycles
            - Bit24-31:采样点
        :param btrCfgData:int 数据场的配置 为 0 非必须
        :param timeOffsetBrsNs:int brs 场的时间偏移 非必须
        :param timeOffsetCrcDelNs:int time offset of crc delimiter field 非必须
        :param bitCount:int 完整的数据长度 非必须
        :param dir:int message 的方向
        :param extDataOffset:int 如果 extDataOffset 使用的话，其偏移 非必须
        :param crc:int message 的 crc 非必须
        :param data:list[int] message 数据
        '''
        super().__init__()
        self.channel = channel
        self.dlc = dlc
        self.validDataBytes = validDataBytes
        self.txCount = txCount
        self.id = id
        self.frameLength = frameLength
        self.flags = flags
        self.btrCfgArb = btrCfgArb
        self.btrCfgData = btrCfgData
        self.timeOffsetBrsNs = timeOffsetBrsNs
        self.timeOffsetCrcDelNs = timeOffsetCrcDelNs
        self.dir = dir
        self.extDataOffset = extDataOffset
        self.crc = crc
        self.data = (ctypes.c_uint8 * 64)(*data)
        self._dataLength = len(data)
        self._blfObjType = BLF_ObjectType.CAN_FD_MESSAGE_64

    
    def ToDict(self) -> dict:
        # return super().ToDict()
        # print('channel.type {0}, data.type {1}'.format(type(self.channel), type(list(ctypes.string_at(self.data, self._dataLength))[0])))
        d_ = super().ToDict()
        d_.update({
            'channel': self.channel,
            'dlc': self.dlc,
            'validDataBytes': self.validDataBytes,
            'txCount': self.txCount,
            'id': self.id,
            'frameLength': self.frameLength,
            'flags': self.flags,
            'btrCfgArb': self.btrCfgArb,
            'btrCfgData': self.btrCfgData,
            'timeOffsetBrsNs': self.timeOffsetBrsNs,
            'timeOffsetCrcDelNs': self.timeOffsetCrcDelNs,
            'dir': self.dir,
            'extDataOffset': self.extDataOffset,
            'crc': self.crc,
            'data': list(ctypes.string_at(self.data, self._dataLength)),
        })
        return d_

    # def ToBytes(self) -> bytes:
    #     return super().ToBytes()\
    #         + self._dataLength.to_bytes(2, byteorder='big', signed=False) \
    #         + self.channel.to_bytes(1, byteorder='big', signed=False) \
    #         + self.dlc.to_bytes(1, byteorder='big', signed=False) \
    #         + self.validDataBytes.to_bytes(1, byteorder='big', signed=False) \
    #         + self.txCount.to_bytes(1, byteorder='big', signed=False) \
    #         + self.id.to_bytes(4, byteorder='big', signed=False) \
    #         + self.frameLength.to_bytes(4, byteorder='big', signed=False) \
    #         + self.flags.to_bytes(4, byteorder='big', signed=False) \
    #         + self.btrCfgArb.to_bytes(4, byteorder='big', signed=False) \
    #         + self.btrCfgData.to_bytes(4, byteorder='big', signed=False) \
    #         + self.timeOffsetBrsNs.to_bytes(4, byteorder='big', signed=False) \
    #         + self.timeOffsetCrcDelNs.to_bytes(4, byteorder='big', signed=False) \
    #         + self.dir.to_bytes(1, byteorder='big', signed=False) \
    #         + self.extDataOffset.to_bytes(1, byteorder='big', signed=False) \
    #         + self.crc.to_bytes(4, byteorder='big', signed=False) \
    #         + bytes(list(ctypes.string_at(self.data, self._dataLength))) \

class CanMessagePy(BlfIoStruct):
    _fields_ =[
        ('channel', ctypes.c_uint8),
        ('flags', ctypes.c_uint8),
        ('dlc', ctypes.c_uint8),
        ('id', ctypes.c_uint8),
        ('data', ctypes.c_uint8*8),
        ('_dataLength', ctypes.c_uint16),
    ]
    def __init__(
        self,
        channel:int = 0,
        flags:int = 0,
        dlc:int=0,
        id:int=0,
        data:typing.List[int]=[]) -> None:
        '''
        CanMessage Object
        :param channel:int 通道
        :param flags:int
            - Bit 0:TX
            - Bit 5:NERR
            - Bit 6:WU
            - Bit 7:RTR
        :param dlc:int dlc
        :param id:int id
        :param data:list[int] 需要和dlc匹配
        '''
        super().__init__()
        self.channel = channel
        self.flags = flags
        self.dlc = dlc
        self.id = id
        self.data = (ctypes.c_uint8 * 8)(*data)
        self._dataLength = len(data)
        self._blfObjType = BLF_ObjectType.CAN_MESSAGE

    def ToDict(self) -> dict:
        # return super().ToDict()
        d_ = super().ToDict()
        d_.update({
            'channel': self.channel,
            'flags': self.flags,
            'dlc': self.dlc,
            'id': self.id,
            'data': list(ctypes.string_at(self.data, self._dataLength)),
        })
        return d_

class CanMessage2Py(BlfIoStruct):
    _fields_ =[
        ('channel', ctypes.c_uint16),
        ('flags', ctypes.c_uint8),
        ('dlc', ctypes.c_uint8),
        ('id', ctypes.c_uint32),
        ('data', ctypes.c_uint8*8),
        ('frameLength', ctypes.c_uint32),
        ('bitCount', ctypes.c_uint8),
        ('reservedCanMessage1', ctypes.c_uint8),
        ('reservedCanMessage2', ctypes.c_uint16),
        ('_dataLength', ctypes.c_uint16),
    ]
    def __init__(
        self,
        channel:int=0,
        flags:int=0,
        dlc:int=0,
        id:int=0,
        data:typing.List[int]=[],
        frameLength:int=0,
        bitCount:int=0,
        reservedCanMessage1:int=0,
        reservedCanMessage2:int=0) -> None:
        super().__init__()
        '''
        CanMessage2 Object
        :param channel:int channel
        :param flags:int
            - Bit 0:TX
            - Bit 5:NERR
            - Bit 6:WU
            - Bit 7:RTR
        :param dlc:int dlc
        :param id:int id
        :param data:list[int] 需要和dlc匹配
        :param frameLength:int 报文长度 非必须
        :param bitCount:int 报文完成的 Bit 长度 非必须
        :param reservedCanMessage1:int 保留
        :param reservedCanMessage2:int 保留
        '''
        self.channel = channel
        self.flags = flags
        self.dlc = dlc
        self.id = id
        self.data = (ctypes.c_uint8*8)(*data)
        self.frameLength = frameLength
        self.bitCount = bitCount
        self.reservedCanMessage1 = reservedCanMessage1
        self.reservedCanMessage2 = reservedCanMessage2
        self._dataLength = len(data)
        self._blfObjType = BLF_ObjectType.CAN_MESSAGE2

    def ToDict(self) -> dict:
        d_ = super().ToDict()
        d_.update({
            'channel': self.channel,
            'flags': self.flags,
            'dlc': self.dlc,
            'id': self.id,
            'data': list(ctypes.string_at(self.data, self._dataLength)),
            'frameLength': self.frameLength,
            'bitCount': self.bitCount,
            'reservedCanMessage1': self.reservedCanMessage1,
            'reservedCanMessage2': self.reservedCanMessage2,
        })
        return d_

class LinMessagePy(BlfIoStruct):
    _fields_ =[
        ('channel', ctypes.c_uint16),
        ('id', ctypes.c_uint8),
        ('dlc', ctypes.c_uint8),
        ('data', ctypes.c_uint8*8),
        ('fsmId', ctypes.c_uint8),
        ('fsmState', ctypes.c_uint8),
        ('headerTime', ctypes.c_uint8),
        ('fullTime', ctypes.c_uint8),
        ('crc', ctypes.c_uint16),
        ('dir', ctypes.c_uint8),
        ('reservedLinMessage1', ctypes.c_uint8),
        ('reservedLinMessage2', ctypes.c_uint32),
        ('_dataLength', ctypes.c_uint16),
    ]
    def __init__(
        self,
        channel:int=0,
        id:int=0,
        dlc:int=0,
        data:typing.List[int]=[],
        fsmId:int=0,
        fsmState:int=0,
        headerTime:int=0,
        fullTime:int=0,
        crc:int=0,
        dir:int=0,
        reservedLinMessage1:int=0,
        reservedLinMessage2:int=0) -> None:
        '''
        LinMessage Object
        :param channel:int channel
        :param id:int lin id
        :param dlc:int dlc
        :param data:list[int] 数据
        :param fsmId:int Slave Identifier in the Final State Machine
        :param fsmState:int State Identifier of a Slave in the Final State
        :param headerTime:int Duration of the frame header [in bit times]
        :param fullTime:int Duration of the entire frame [in bit times]
        :param crc:int crc
        :param dir:int 0:Rx 1:Tx 2:Tx Request
        :param reservedLinMessage1: 保留
        :param reservedLinMessage2: 保留
        '''
        super().__init__()
        self.channel = channel
        self.id = id
        self.dlc = dlc
        self.data = (ctypes.c_uint8*8)(*data)
        self._dataLength = min(len(data), 8)
        self.fsmId = fsmId
        self.fsmState = fsmState
        self.headerTime = headerTime
        self.fullTime = fullTime
        self.crc = crc
        self.dir = dir
        self.reservedLinMessage1 = reservedLinMessage1
        self.reservedLinMessage2 = reservedLinMessage2
        self._blfObjType = BLF_ObjectType.LIN_MESSAGE

    def ToDict(self) -> dict:
        d_ = super().ToDict()
        d_.update({
            'channel': self.channel,
            'id': self.id,
            'dlc': self.dlc,
            'data': list(ctypes.string_at(self.data, self._dataLength)),
            'fsmId': self.fsmId,
            'fsmState': self.fsmState,
            'headerTime': self.headerTime,
            'fullTime': self.fullTime,
            'crc': self.crc,
            'dir': self.dir,
            'reservedLinMessage1': self.reservedLinMessage1,
            'reservedLinMessage2': self.reservedLinMessage2,
        })
        return d_

class LinMessage2Py(BlfIoStruct):
    _fields_ =[
        ('data', ctypes.c_uint8*8),
        ('crc', ctypes.c_uint16),
        ('dir', ctypes.c_uint8),
        ('simulated', ctypes.c_uint8),
        ('isEtf', ctypes.c_uint8),
        ('etfAssocIndex', ctypes.c_uint8),
        ('etfAssocEtfId', ctypes.c_uint8),
        ('fsmId', ctypes.c_uint8),
        ('fsmState', ctypes.c_uint8),
        ('reservedLinMessage1', ctypes.c_uint8),
        ('reservedLinMessage2', ctypes.c_uint16),
        ('respBaudrate', ctypes.c_uint32),
        ('exactHeaderBaudrate', ctypes.c_double),
        ('earlyStopbitOffset', ctypes.c_uint32),
        ('earlyStopbitOffsetResponse', ctypes.c_uint32),
        ('apiMajor', ctypes.c_uint8),
        ('_dataLength', ctypes.c_uint16),
    ]
    def __init__(
        self,
        data:typing.List[int]=[],
        crc:int=0,
        dir:int=0,
        simulated:int=0,
        isEtf:int=0,
        etfAssocIndex:int=0,
        etfAssocEtfId:int=0,
        fsmId:int=0,
        fsmState:int=0,
        reservedLinMessage1:int=0,
        reservedLinMessage2:int=0,
        respBaudrate:int=0,
        exactHeaderBaudrate:float=0.0,
        earlyStopbitOffset:int=0,
        earlyStopbitOffsetResponse:int=0,
        apiMajor:int=3,        
        ) -> None:
        '''
        LinMessage2 Object
        :param data:list[int] 数据
        :param crc:int crc
        :param dir:int 0:Rx 1:Tx 2:Tx Request
        :param simulated:int 0:真报文 1:仿真报文
        :param isEtf:int Flag indicating whether this frame is Event-Triggered one
            - 0:not ETF
            - 1:ETF
        :param etfAssocIndex:int Unconditional frame associated with ETF - serial index
        :param etfAssocEtfId:int Unconditional frame associated with ETF - id of ETF
        :param fsmId:int Slave Identifier in the Final State
        :param fsmState:int State Identifier of a Slave in the
        :param reservedLinMessage1:int 保留
        :param reservedLinMessage2:int 保留
        :param respBaudrate:int Response baudrate of the event in bit/sec
        :param exactHeaderBaudrate:double Exact baudrate of the header in bit/sec
        :param earlyStopbitOffset:int Early stop bit offset for UART timestamps in ns
        :param earlyStopbitOffsetResponse:int Early stop bit offset in frame response for UART timestamps in ns
        :param apiMajor:int API major number (see FileStatistics)
        '''
        super().__init__()
        self.data = (ctypes.c_uint8*8)(*data)
        self._dataLength = min(len(data), 8)
        self.crc = crc
        self.dir = dir
        self.simulated = simulated
        self.isEtf = isEtf
        self.etfAssocIndex = etfAssocIndex
        self.etfAssocEtfId = etfAssocEtfId
        self.fsmId = fsmId
        self.fsmState = fsmState
        self.reservedLinMessage1 = reservedLinMessage1
        self.reservedLinMessage2 = reservedLinMessage2
        self.respBaudrate = respBaudrate
        self.exactHeaderBaudrate = exactHeaderBaudrate
        self.earlyStopbitOffset = earlyStopbitOffset
        self.earlyStopbitOffsetResponse = earlyStopbitOffsetResponse
        self.apiMajor = apiMajor
        self._blfObjType = BLF_ObjectType.LIN_MESSAGE2

    def ToDict(self) -> dict:
        d_ = super().ToDict()
        d_.update({
            'data': list(ctypes.string_at(self.data, self._dataLength)),
            'crc': self.crc,
            'dir': self.dir,
            'simulated': self.simulated,
            'isEtf': self.isEtf,
            'etfAssocIndex': self.etfAssocIndex,
            'etfAssocEtfId': self.etfAssocEtfId,
            'fsmId': self.fsmId,
            'fsmState': self.fsmState,
            'reservedLinMessage1': self.reservedLinMessage1,
            'reservedLinMessage2': self.reservedLinMessage2,
            'respBaudrate': self.respBaudrate,
            'exactHeaderBaudrate': self.exactHeaderBaudrate,
            'earlyStopbitOffset': self.earlyStopbitOffset,
            'earlyStopbitOffsetResponse': self.earlyStopbitOffsetResponse,
            'apiMajor': self.apiMajor,
        })
        return d_

class EthernetFramePy(BlfIoStruct):
    _fields_ =[
        ('sourceAddress', ctypes.c_uint8*6),
        ('channel', ctypes.c_uint16),
        ('destinationAddress', ctypes.c_uint8*6),
        ('dir', ctypes.c_uint16),
        ('type', ctypes.c_uint16),
        ('tpid', ctypes.c_uint16),
        ('tci', ctypes.c_uint16),
        ('payLoadLength', ctypes.c_uint16),
        ('reservedEthernetFrame', ctypes.c_uint64),
        ('payLoad', ctypes.c_uint8*65535),
        ('_payloadLength', ctypes.c_uint16),
    ]
    def __init__(
        self,
        sourceAddress:typing.List[int]=[0,0,0,0,0,0],
        channel:int=0,
        destinationAddress:typing.List[int]=[0,0,0,0,0,0],
        dir:int=0,
        type:int=0,
        tpid:int=0,
        tci:int=0,
        payLoadLength:int=0,
        reservedEthernetFrame:int=0,
        payLoad:typing.List[int]=[]) -> None:
        super().__init__()
        '''
        EthernetFramePy Object
        :param sourceAddress:list[int] 源地址
        :param channel:int channel
        :param destinationAddress:list[int] 目的地址
        :param dir:int 方向
            - 0:Rx
            - 1:Tx
            - 2:TxRq
        :param type:int EtherType which indicates protocol for Ethernet payload data, See Ethernet standard specification for valid values
        :param tpid:int TPID when VLAN tag valid, zero when no VLAN. See Ethernet standard specification.
        :param tci:int TCI when VLAND tag valid, zero when no VLAN. See Ethernet standard specification.
        :param payLoadLength:int Number of valid payLoad bytes Length of Ethernet payload data in bytes. Max. 1500 Bytes (without Ethernet header)
        :param reservedEthernetFrame:int 保留
        :param payLoad:list[int] payLoad Max 1500 data bytes per frame Ethernet payload data (without Ethernet header)
        '''
        self.sourceAddress = (ctypes.c_uint8*6)(*sourceAddress)
        self.channel = channel
        self.destinationAddress = (ctypes.c_uint8*6)(*destinationAddress)
        self.dir = dir
        self.type = type
        self.tpid = tpid
        self.tci = tci
        self.payLoadLength = payLoadLength
        self.reservedEthernetFrame = reservedEthernetFrame
        self.payLoad = (ctypes.c_uint8*65535)(*payLoad)
        self._payloadLength = len(payLoad)
        self._blfObjType = BLF_ObjectType.ETHERNET_FRAME

    def ToDict(self) -> dict:
        # return super().ToDict()
        d_ = super().ToDict()
        d_.update({
            'sourceAddress': list(ctypes.string_at(self.sourceAddress, 6)),
            'channel': self.channel,
            'destinationAddress': list(ctypes.string_at(self.destinationAddress, 6)),
            'dir': self.dir,
            'type': self.type,
            'tpid': self.tpid,
            'tci': self.tci,
            'payLoadLength': self.payLoadLength,
            'reservedEthernetFrame': self.reservedEthernetFrame,
            'payLoad': list(ctypes.string_at(self.payLoad, self._payloadLength)),
        })
        return d_


