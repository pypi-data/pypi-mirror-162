# -*- coding: utf-8 -*
'''
Created on 18.09.2018

@author:
'''
import datetime
from datetime import datetime, timedelta
from time import localtime, strftime, time, sleep

from general.ConnectorHID import Connector
import platform
from application.defines import define as const
import struct
from application.defines import DEFINES_KEY_EVENT as EVENT
from application.defines import DEFINES_KEY as KEY
from application.defines import DEFINES_SERVICE_TYPE as SERVICE_TYPE
from application.defines import DEFINES_MEAS_TYPE as MEAS_TYPE

SECONDS_A_DAY = 24 * 60 * 60
EXECUTE_REQUEST_MAX_TRIES = 5

class Commands(Connector):

    def __init__(self):
        print(platform.system())
        if platform.system() == 'Windows':
            from devices.ConnectorHIDWin import Connector_HID_Win
            self.hid_interface =  Connector_HID_Win(const.Vendor_ID, const.Product_ID_5820)
        else:
            from devices.ConnectorHIDLinux import Connector_HID_Linux
            self.hid_interface = Connector_HID_Linux(const.Vendor_ID, const.Product_ID_5820)

    def get_meas_result(self):
        value = 0.0
        test = 1.0
        pafFlag = False
        ack, result = self.hid_interface.sendCommand(87)
        value = struct.unpack('I', bytearray(result[2:6]))
        value = value[0]/(10**result[6])
        return ack, value, result[8],  result[7]

    def get_meas_result_error(self):
        ack, result = self.hid_interface.sendCommand(87)
        return ack, result[0], result[1]

    def get_device_data(self):
        ack, result = self.hid_interface.sendCommand(48)
        value_1 = result[:9]
        value_2 = result[10:18]
        serialnumber = ''.join(chr(e) for e in value_1)
        partnumber = ''.join(chr(e) for e in value_2)
        return self.__to_bytes(partnumber), self.__to_bytes(serialnumber)

    def get_device_status(self):
        ack, result = self.hid_interface.sendCommand(2)
        return ack, self.__to_bytes(result)

    def get_meas_status(self):
        ack, result = self.hid_interface.sendCommand(71)
        return ack, self.__to_bytes(result)

    def get_last_error(self):
        return self.hid_interface.get_last_error()

    def key_OK_short_pressed(self):
        return self.__key_pressed(KEY.OK, EVENT.SHORT)

    def key_OK_down(self):
        return self.__key_pressed(KEY.OK, EVENT.DOWN)

    def key_OK_up(self):
        return self.__key_pressed(KEY.OK, EVENT.UP)

    def key_OK_long_pressed(self):
        return self.__key_pressed(KEY.OK, EVENT.LONG)

    def device_reset(self):
        ack, result = self.hid_interface.sendCommand(1)
        return ack

    def get_adjustment_information(self):
        ack, utc = self.__get_serv_information(SERVICE_TYPE.ADJUSTMENT)
        return ack, strftime("%Y-%m-%d %H:%M:%S", localtime(utc))

    def get_acc_information(self):
        ack, utc = self.__get_serv_information(SERVICE_TYPE.ACCURACY_CHECK)
        return ack, strftime("%Y-%m-%d %H:%M:%S", localtime(utc))

    def get_service_information(self):
        ack, utc = self.__get_serv_information(SERVICE_TYPE.SERVICE)
        return ack, strftime("%Y-%m-%d %H:%M:%S", localtime(utc))

    def get_current_flow(self):
        ack, result = self.hid_interface.sendCommand(96)
        try:
            flow = struct.unpack('f', bytearray(result))[0]
        except:
            flow = 0.0
            ack = False
        return ack, flow

    def trigger_sample_unit(self):
        ack, result = self.hid_interface.sendCommand(69)
        return ack

    def start_breathtest(self):
        return self.__device_meas_start(MEAS_TYPE.BREATHTEST)

    def start_adjustment(self):
        return self.__device_meas_start(MEAS_TYPE.ADJUSTMENT)

    def start_acc(self):
        return self.__device_meas_start(MEAS_TYPE.ACCURACY_CHECK)

    def __get_serv_information(self, type):

        data = []
        data.append(type)  # id (adj, acc, serv)

        ack, result = self.hid_interface.sendCommand(185, data)
        utc = result[0] + (result[1] << 8) + (result[2]<< 16) + (result[3] << 24)
        return ack, utc

    def __device_meas_start(self, type):

        data = []
        data.append(type)  # id (breathtest, adj, acc, serv)

        ack, result = self.hid_interface.sendCommand(66, data)
        return ack, self.__to_bytes(result)

    def __key_pressed(self, buttom, event):
        data = []
        data.append(buttom)  # Button id
        data.append(event)  # Button event

        ack, result = self.hid_interface.sendCommand(41, data)
        return ack

    def __to_bytes(self, bytes_or_string):
        if isinstance(bytes_or_string, str):
            value = bytes_or_string.encode()
        else:
            bytes_or_string.append(0)
            value = bytes_or_string[0]
        return value

    def is_deviced_connected(self):
        ret = self.hid_interface.is_device_open()
        return ret

    def get_recovery_time(self):

        for _ in range(EXECUTE_REQUEST_MAX_TRIES):
            try:
                ack, recovery_time = self.hid_interface.sendCommand(89)
                time_left = struct.unpack("<L", bytearray(recovery_time))[0]
                break
            except Exception as e:
                print(str(e))
                sleep(1)
        return ack, time_left

    def device_getCurrentDateTime(self):
        result = self.hid_interface.sendCommand(32)[1]
        utc = struct.unpack("<I", bytearray(result[0:4]))[0]
        return utc

    def __create_cfg_and_deviceData_command(self, token, cmd_id):
        filelength = 16
        data = []
        token = token
        cmd_id = cmd_id
        value = b'\0'
        for element in token:
            data.append(ord(element))
        for index in range(3, filelength):
            data.extend(value)
        command = struct.pack('I', cmd_id)
        data.extend(command)
        return data

    def device_lastAdjustment(self):
        data = self.__create_cfg_and_deviceData_command("dev", 4)
        result = self.hid_interface.sendCommand(12, data)[1]
        utc = struct.unpack("<I", bytearray(result[20:24]))[0]
        return utc

    def device_adjAccIntervals(self):
        data = self.__create_cfg_and_deviceData_command("dev", 31)
        result = self.hid_interface.sendCommand(12, data)[1]
        adjlastInterval = struct.unpack("<h", bytearray(result[20:22]))[0]
        acclastInterval = struct.unpack("<h", bytearray(result[22:24]))[0]
        return adjlastInterval, acclastInterval

    def get_calibration_days_left(self):
        lastAdjDate = self.device_lastAdjustment()
        adjInterval = self.device_adjAccIntervals()[0]
        deviceDateTime = datetime.utcfromtimestamp(self.device_getCurrentDateTime())

        lastAdjDate = datetime.utcfromtimestamp(lastAdjDate)
        end_date = lastAdjDate + timedelta(days=adjInterval)

        days_To_Calibration = end_date - deviceDateTime
        count = days_To_Calibration.days + 1
        return count
