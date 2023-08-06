# -*- coding: utf-8 -*
'''
Created on 18.09.2019

@author: schirrje

'''
class define:
	MEAS_STATE_STOPPED        	= 0 # Measurement System is stopped
	MEAS_STATE_PREPARATION    	= 1 # Measurement System prepares for a new measurement
	MEAS_STATE_PREPARATION_DONE = 2 # Measurement System is ready for a Blowrequest
	MEAS_STATE_BLOWREQUEST    	= 3 # Measurement System Blowrequest
	MEAS_STATE_BLOWING        	= 4 # Blow phase
	MEAS_STATE_ANALYZING      	= 5 # Analyzing phase
	MEAS_STATE_RESULT         	= 6 # Result is available
	MEAS_STATE_BLANKCHECK     	= 7 # Blankcheck is running
	MEAS_STATE_STANDBY        	= 8 # Measurement System is in Standby

	MEAS_CLASS_IDLE 			= 0 #Currently not specified
	MEAS_CLASS_1 				= 1 #Class	1
	MEAS_CLASS_2 				= 2 #Class	2
	MEAS_CLASS_3 				= 3 #Class	3
	MEAS_CLASS_4 				= 4 #Class	4
	MEAS_CLASS_5 				= 5 #Class	5
	MEAS_CLASS_6 				= 6 #Class	6
	MEAS_CLASS_OVERRANGE 		= 7 #Overrange
	MEAS_CLASS_NO_ALCOHOL 		= 8 #Passive	No	Alcohol
	MEAS_CLASS_ALCOHOL 			= 9 #Passive	Alcohol
	MEAS_CLASS_PASS 			= 10 #Class	Pass(Used for accuracy check)
	MEAS_CLASS_FAIL 			= 11 # Class	Fail(Used for accuracy check)
	MEAS_CLASS_INVALID 			= 12 # Not	classified.

	Vendor_ID = 0x0891
	Product_ID_5820 = 0x8121
	Product_ID_3820 = 0x8122
	Product_ID_5000 = 0x8123
	Product_ID_4000 = 0x8124
	Product_ID_6000 = 0x8125
	Product_ID_ACE  = 0x8126

class DEFINES_KEY_EVENT:
	DOWN  = 1 # key  down
	UP    = 2 # key up
	SHORT = 3 # key short pressed
	LONG  = 4 # key long pressed

class DEFINES_KEY:
	OK    = 0 # key OK
	UP    = 1 # key up
	DOWN  = 2 # key down

class DEFINES_SERVICE_TYPE:
	ADJUSTMENT      = 0 #
	ACCURACY_CHECK  = 1 #
	SERVICE         = 2 #

class DEFINES_MEAS_TYPE:
	BREATHTEST      = 0 #
	ADJUSTMENT      = 1 #
	ACCURACY_CHECK  = 2 #
