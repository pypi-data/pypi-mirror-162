# -*- coding: utf-8 -*
'''
Created on 18.09.2019

@author:
'''

from general.ConnectorHID import Connector
import pywinusb.hid as hid
import time


class Connector_HID_Win(Connector):
    __my_buffer = []
    def __readData(self, data):
        self.__my_buffer = []
        for d in data:
            self.__my_buffer.append(d)

    def close(self):
        if self.__is_open():
            try:
                self.hidDevice.close()
            except:
                print('device not connected')
            super().close()


    def open(self):
        # Find device
        ret = True
        if not self.__is_open():
            # VID and PID customization changes here...
            filter = hid.HidDeviceFilter(vendor_id=self.vendorID, product_id=self.productID)
            hid_device = filter.get_devices()
            try:
                self.hidDevice = hid_device[0]
                self.hidDevice.open()
                print("opened")
                print(hid_device)
            except:
                self.last_error = 'No device found'
                print(self.last_error)
                ret = False
        return ret

    def executeWrite(self, request):
        super().executeWrite(request)
        if not self.hidDevice:
            self.last_error = 'No device found'
        else:
            self.__my_buffer = []
            target_usage = hid.get_full_usage_id(0x00, 0x3f)
            self.hidDevice.set_raw_data_handler(self.__readData)

            report = self.hidDevice.find_output_reports()[0]
            print(report)
            buffer = [0x00]   # USB packet size
            buffer = buffer + request
            dummy = [0x00] * ( 65 - len(buffer))
            buffer = buffer + dummy
            report.set_raw_data(buffer)
            report.send()
            time.sleep(0.1)

    def executeRead(self):
        print("executeRead")
        # read the data
        try:
            return self.unpackResponse(self.__my_buffer[2:(self.__my_buffer[1] + 2)])  # first byte is the length of the complete message
        except:
            self.last_error = 'data error'
            print(self.__my_buffer)
            return


    def __is_open(self):
        return self.hidDevice != 0

    def is_device_open(self):
        return self.__is_open()

