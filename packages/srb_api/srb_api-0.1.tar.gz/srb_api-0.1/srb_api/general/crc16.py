# -*- coding: utf-8 -*
'''
Created on 07.09.2018

@author:
'''

class CRC16:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def CalcCCITT_crc16(self, buff={}):
        crc = 0x0000
        if buff != 0:
            for i in buff:
                c = i
                q = (crc ^ c) & 0x0f
                crc = (crc >> 4) ^ (q * 0x1081)
                q = (crc ^ (c >> 4)) & 0xf
                crc = (crc >> 4) ^ (q * 0x1081)
        else:
            crc = 0
        return crc
