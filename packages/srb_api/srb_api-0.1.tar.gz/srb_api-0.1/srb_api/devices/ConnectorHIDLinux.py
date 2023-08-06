# -*- coding: utf-8 -*#
'''
Created on 18.09.2019

@author:
'''

from general.ConnectorHID import Connector
import usb.core
import sys

class Connector_HID_Linux(Connector):

    def open(self):
        # Find device
        ret = True
        if not self.__is_open():
            self.hidDevice = usb.core.find(idVendor=self.vendorID, idProduct=self.productID)

            if not self.hidDevice:
                self.last_error ="No device connected"
                ret = False
            else:
                print('device connected')
                if self.hidDevice.is_kernel_driver_active(0):
                    try:
                        self.hidDevice.detach_kernel_driver(0)
                    except usb.core.USBError as e:
                        self.last_error = 'Could not detatch kernel driver'
                        sys.exit("Could not detatch kernel driver: %s" % str(e))
                try:
                    self.hidDevice.set_configuration()
                    self.hidDevice.reset()
                    self.endpointRead = self.hidDevice[0][(0, 0)][0]
                    self.endpointWrite = self.hidDevice[0][(0, 0)][1]
                    print("opened")
                except usb.core.USBError as e:
                    self.last_error = "Could not set configuration: %s" % str(e)
                    ret = False
        return ret

    def close(self):
        try:
            usb.util.dispose_resources(self.hidDevice)
        except:
            True
        super().close()

    def executeWrite(self, request ):
        super().executeWrite(request)
        response = 0
        print("executeWrite")
        try:
            response = self.hidDevice.write(self.endpointWrite.bEndpointAddress, request)
        except:
            self.last_error = 'Comerror !'
            raise
        return response

    def executeRead(self):
        print("executeRead")
        # read the data
        data = []
        try:
            data = self.hidDevice.read(self.endpointRead.bEndpointAddress, 64)
        except usb.core.USBError as e:
            if e.errno == 110:  # 110 is a timeout.
                self.last_error = 'read Error timeout'
                sys.exit("read Error timeout: %s" % str(e))
        return self.unpackResponse(data[1:(data[0]+1)]) #first byte is the length of the complete message

    def __is_open(self):
        ret = False
        if (self.endpointWrite and self.endpointRead) != 0:
            ret = True
        return ret

