import enum

import nanosurf.lib.spm  as spm

class I2CBusID(enum.IntEnum):
    Unassigned = -1
    User      = 0x2000300
    HV        = 0x2000320
    ScanHead  = 0x2000360
    Interface = 0x2000340

class I2CInstances(enum.IntEnum):
    MAIN_APP = 0
    CONTROLLER = 1

class I2CMasterType(enum.IntEnum):
    AUTO_DETECT = -1
    EMBEDDED_AVALON = 0
    ACCESSORY_MASTER = 1
    EMBEDDED_LINUX = 2

class I2CBusSpeed(enum.IntEnum):
    kHz_Default = 0
    kHz_100 = 1
    kHz_200 = 2
    kHz_400 = 3

class I2CSyncing(enum.IntEnum):
    NoSync = 0
    Sync = 1
    
class I2CByteMode(enum.IntEnum):
    SingleByteOff = 0
    SingleByteOn = 1

class I2COffsetMode(enum.IntEnum):
    NoOffset = 0
    U8Bit = 1
    U16Bit_MSBFiRST = 2
    U16Bit_LSBFiRST = 3
    
class I2CBusMaster():
        
    _active_chip_ref = int(0)
    _next_chip_ref = 1

    def __init__(self, spm_ctrl: spm.Spm, bus_id: I2CBusID, instance_id: I2CInstances = I2CInstances.CONTROLLER, master_type: I2CMasterType = I2CMasterType.AUTO_DETECT, bus_speed: I2CBusSpeed = I2CBusSpeed.kHz_400):
        self.spm_ctrl = spm_ctrl
        self._test_obj = self.spm_ctrl.application.CreateTestObj
        self._rx_packet_buffer_len = 50
        self._tx_packet_buffer_len = 50
        self._instance_id = instance_id
        self._master_type = master_type 
        self._bus_id = bus_id
        self._bus_speed = bus_speed
        if self._master_type == I2CMasterType.AUTO_DETECT:
            self._master_type = self._auto_set_bus_master()

    def assign_i2c_bus(self,  bus_id: I2CBusID, bus_speed: I2CBusSpeed):
        self._bus_id = bus_id
        self._bus_speed = bus_speed

    def assign_chip(self, chip: 'I2CChip'):
        chip.setup_bus_connection(self, self.create_unique_chip_id())

    def setup_metadata(self, addr: int, offset_mode: I2COffsetMode, auto_lock: bool = True):
        self._test_obj.I2CSetupMetaDataEx(self._rx_packet_buffer_len, self._tx_packet_buffer_len, I2CSyncing.NoSync, I2CByteMode.SingleByteOff, self._bus_speed)
        self._test_obj.I2CSetupMetaData(self._instance_id, self._master_type, self._bus_id, addr, offset_mode, auto_lock)

    def check_connection(self, chip: 'I2CChip') -> bool:
        self.activate_chip(chip)
        is_connected:int = self._test_obj.I2CIsConnected
        return is_connected > 0

    @classmethod
    def get_active_chip_id(cls) -> int:
        return I2CBusMaster._active_chip_ref

    @classmethod
    def create_unique_chip_id(cls) -> int:
        I2CBusMaster._next_chip_ref += 1
        return I2CBusMaster._next_chip_ref

    def activate_chip(self, chip: 'I2CChip'):
        if chip.get_chip_ref() != I2CBusMaster._active_chip_ref:
            chip.activate()
            I2CBusMaster._active_chip_ref = chip.get_chip_ref()

    def write_bytes(self, offset: int, data: list[int]) -> bool:
        done = False
        try:
            done: bool = self._test_obj.I2CWrite(offset, len(data),data)
        except:
            pass
        return done

    def read_bytes(self, offset:int, data_count:int) -> list[int]:
        try:
            data: list[int] = self._test_obj.I2CReadEx(offset, data_count) # read content
        except:
            data: list[int] = []
        return data

    def _auto_set_bus_master(self) -> I2CMasterType:
        detected_master = I2CMasterType.AUTO_DETECT

        if self._instance_id == I2CInstances.CONTROLLER:
            if self.spm_ctrl.get_controller_type() == self.spm_ctrl.ControllerType.CX:
                if self.spm_ctrl.get_firmware_type() == self.spm_ctrl.FirmwareType.LINUX:
                    if self._bus_id == I2CBusID.User:
                        detected_master = I2CMasterType.EMBEDDED_AVALON
                    else:
                        detected_master = I2CMasterType.EMBEDDED_LINUX
                else:
                    detected_master = I2CMasterType.EMBEDDED_AVALON
        elif self._instance_id == I2CInstances.MAIN_APP:
            detected_master = I2CMasterType.ACCESSORY_MASTER

        return detected_master

class I2CChip():

    def __init__(self, bus_addr: int, offset_mode: I2COffsetMode, name: str = "", bus_master: I2CBusMaster = None, auto_lock: bool = True):
        """ Minimal initialization is bus_addr and offset_mode. connection to bus master can be done later by bus_master.assign_chip() """
        self._bus_master = bus_master
        self._chip_ref = -1
        self.name = name
        self.bus_address = bus_addr
        self.offset_mode = offset_mode
        self.auto_lock = auto_lock
        if self._bus_master is not None:
            self._bus_master.assign_chip(self)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name:str):
        self.__name = name

    @property
    def bus_address(self) -> int:
        return self.__bus_addr

    @bus_address.setter
    def bus_address(self, addr: int):
        self.__bus_addr = addr

    @property
    def offset_mode(self) -> I2COffsetMode:
        return self.__offset_mode

    @offset_mode.setter
    def offset_mode(self, mode: I2COffsetMode):
        self.__offset_mode = mode

    @property
    def auto_lock(self) -> bool:
        return self.__auto_lock

    @auto_lock.setter
    def auto_lock(self, lock:bool):
        self.__auto_lock = lock

    def setup_bus_connection(self, bus_master: I2CBusMaster, chip_ref: int):
        self._bus_master = bus_master
        self._chip_ref = chip_ref

    def activate(self):
        self._bus_master.setup_metadata(self.bus_address, self.offset_mode, self.auto_lock)

    def get_chip_ref(self) -> int:
        return self._chip_ref

    def get_bus(self):
        self._bus_master.activate_chip(self)

    def is_connected(self) -> bool:
        return self._bus_master.check_connection(self)

    def write_bytes_with_offset(self, offset: int, data: list[int]) -> bool:
        self.get_bus()
        done = self._bus_master.write_bytes(offset, data)
        return done

    def write_byte_with_offset(self, offset:int, data:int) -> bool:
        return self.write_bytes_with_offset(offset, [data])

    def write_bytes(self, data: list[int]) -> bool:
        return self.write_bytes_with_offset(0, data)

    def write_byte(self, data: int) -> bool:
        return self.write_bytes_with_offset(0, [data])

    def read_bytes_with_offset(self, offset:int, count: int) -> list[int]:
        self.get_bus()
        data = self._bus_master.read_bytes(offset, count)
        return data

    def read_byte_with_offset(self, offset: int) -> int:
        data = self.read_bytes_with_offset(offset, count=1)
        return data[0]

    def read_bytes(self, count: int) -> list[int]:
        data = self.read_bytes_with_offset(0, count)
        return data

    def read_byte(self) -> int:
        data = self.read_bytes_with_offset(0, count=1)
        return data[0]

