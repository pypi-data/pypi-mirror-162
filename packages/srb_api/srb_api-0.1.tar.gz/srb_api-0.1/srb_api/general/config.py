# -*- coding: utf-8 -*
'''
Created on 18.09.2019

@author: schirrje

'''
import configparser
import socket

class Config:

    def __init__(self, configfile):
        config = configparser.ConfigParser()
        config.read(configfile)
        self.ip = config['Server']['IP']
        self.port = config['Server']['Port']

    def get_port(self):
        return int(self.port)

    def get_ip_adress(self):
        if self.ip == '0' or self.ip == '':
            ip = 'localhost'
        else:
            ip = self.ip
        return ip