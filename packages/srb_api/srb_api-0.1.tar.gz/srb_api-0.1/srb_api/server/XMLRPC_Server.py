# -*- coding: utf-8 -*
'''
Created on 07.09.2018

@author: schirrje

'''
"""
Einfacher XMLRPC-Server
"""

from xmlrpc.server import SimpleXMLRPCServer
from application.commands import Commands
from general.config import Config
import sys
from application.version import Version_API as v

class XmlrpcHandler:
    command = Commands()

    def get_info_api_part_number(self):
        return v.PARTNUMBER

    def get_info_SW_version(self):
         return v.VERSION

    def get_info_release_date(self):
         return v.RELEASE_DATE

    def get_device_part_number(self):
        partnumber, serialnumber = self.command.get_device_data()
        return partnumber

    def get_device_serial_number(self):
        partnumber, serialnumber = self.command.get_device_data()
        return serialnumber

    def get_meas_result(self):
        return self.command.get_meas_result()

    def get_meas_error(self):
        return self.command.get_meas_result_error()

    def get_meas_status(self):
        return self.command.get_meas_status()

    def get_last_error(self):
        return self.command.get_last_error()

    def device_stop(self):
        return self.command.key_OK_long_pressed()

    def device_start(self):
        return self.command.device_reset()

    def get_service_information(self):
        return self.command.get_service_information()

    def get_adjustment_information(self):
        return self.command.get_adjustment_information()

    def get_acc_information(self):
        return self.command.get_acc_information()

    def get_current_flow(self):
        return self.command.get_current_flow()

    def device_trigger(self):
        #return self.command.trigger_sample_unit() # works only for passiv tests
        return self.command.key_OK_short_pressed()

    def device_start_breathtest(self):
        return self.command.start_breathtest()

    def device_is_device_connected(self):
        return self.command.is_deviced_connected()

    def device_get_recovery_time(self):
        return self.command.get_recovery_time()

    def device_get_calibration_days_left(self):
        return self.command.get_calibration_days_left()



class XmlServer:
    ip_adress = ''
    port      = ''
    try:
        server_config = Config('config.ini')
        ip_adress= server_config.get_ip_adress()
        port = server_config.get_port()
        server = SimpleXMLRPCServer((ip_adress, port))
    except:
        print('ip adress :' + ip_adress)
        print('or ')
        print('port :' + port)
        print('invalid')
        sys.exit()

    server.register_instance(XmlrpcHandler())
    print("The XMLRPC-Server listen to http://" + ip_adress + ':' + str(port) + '.')
    print("For exit press CTRL+C.")
    server.serve_forever()

