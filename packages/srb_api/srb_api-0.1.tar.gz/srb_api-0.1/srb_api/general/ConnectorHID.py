# -*- coding: utf-8 -*
'''
Created on 18.09.2018

@author:
'''

from general.crc16 import CRC16
from random import randint
from time import sleep
import gc

class Connector(object):
    Product_ID = 1
    PROTOCOL_VERSION = 0xC1
    FRAME_HEADER_LENGTH = 0x0B
    FRAME_LENGTH = FRAME_HEADER_LENGTH + 2
    ENUM_ARRAY_GENERIC = 0x03

    def __init__(self, vendorID, productID):
        '''
        Constructor
        '''
        i = 10
        self.endpointRead = 0
        self.endpointWrite = 0
        self.hidDevice = 0
        self.massageID = randint(1, 1000)
        self.vendorID = vendorID
        self.productID = productID
        self.last_error = ''
        while(i):
            ret = self.open()
            if ret == True:
                break
            else:
                if not self.hidDevice:
                    break
                else:
                    sleep(1)
                    i=i-1

    def close(self):
        self.endpointRead = 0
        self.endpointWrite = 0
        self.hidDevice = 0
        print("closed")

    def open(self):
        print('open is not implemented ')

    def get_last_error(self):
        return self.last_error

    def sendCommand(self, cmd, data=[]):
        ack = False

        try:
            gc.collect()
            self.open()
            self.executeWrite(self.createCommand(cmd, data))
            ret = self.executeRead()
            command = ret[0] + (ret[1] << 8)
            if ((command & 0x8000) > 0):
                ack = True
                self.last_error = ''
            return ack, ret[2:]

        except:
            print("write read error")
            self.last_error ='write error'
            self.close()
            ret = [0x00]*64
            return ack, ret

    def executeWrite(self, request):
        self.massageID = self.massageID + 1

    def executeRead(self):
        print('executeRead is not implemented')

    def unpackResponse(self, response=[]):
        data = []
        if len(response) > self.FRAME_LENGTH:
            data = response[self.FRAME_HEADER_LENGTH:-2]  # get databytes without crc
        return data

    def createCommand(self, cmd, data=[]):
            crc = CRC16()
            command = []
            payloadlen = len(data) + 2 # cmd length

            command.extend([self.PROTOCOL_VERSION])
            # Payload
            command.extend([(payloadlen & 0x00FF)])
            command.extend([((payloadlen & 0xFF00) >> 8)])
            # target adress  not used for SRB
            command.extend([0x00])
            command.extend([0x00])
            # source adress  not used for SRB
            command.extend([0x00])
            command.extend([0x00])
            # meassage ID
            command.extend([ (self.massageID & 0x000000FF)])
            command.extend([((self.massageID & 0x0000FF00) >>  8)])
            command.extend([((self.massageID & 0x00FF0000) >> 16)])
            command.extend([((self.massageID & 0xFF000000) >> 24)])

            command.extend([(cmd & 0x00FF)])
            command.extend([((cmd & 0xFF00) >> 8)])
            for d in data:
                command.extend([d])
            checksum = crc.CalcCCITT_crc16(command)
            command.extend([(checksum & 0x00FF)])
            command.extend([((checksum & 0xFF00) >> 8)])

            return [payloadlen + self.FRAME_LENGTH] + command # add first byte (length of the complete message max length 63 byte)





