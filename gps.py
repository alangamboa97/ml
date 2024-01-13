#!/usr/bin/python
# -*- coding:utf-8 -*-
import Jetson.GPIO as GPIO

import serial
import time
import boto3
import json


ser = serial.Serial('/dev/ttyUSB2',115200)
ser.flushInput()

power_key = 6
rec_buff = ''
rec_buff2 = ''
time_count = 0
device_id = 'MyDevice'
FinalLat = 0.0
FinalLong = 0.0



def create_tracker(tracker_name):
    try:
        client =  boto3.client('location',aws_access_key_id='AKIAVUQ3J33Z7NMO7M5S',
                        aws_secret_access_key='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', 
                              region_name='us-east-1')

        response = client.create_tracker(
            TrackerName=tracker_name,
            Description='MyTracker'
        )
        print("Tracker created successfully!")
        return response
    except Exception as e:
        print(f"An error occurred while creating tracker: {e}")
        return None

def start_tracking(tracker_name, device_id, latitude, longitude):
	
    try:
        client =  boto3.client('location',aws_access_key_id='AKIAVUQ3J33Z7NMO7M5S',
                        aws_secret_access_key='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', 
                              region_name='us-east-1')
        response = client.batch_update_device_position(
            TrackerName=tracker_name,
            Updates=[
                {
                    'DeviceId': device_id,
                    'Position': [
                        longitude,  # longitude
                        latitude  # latitude
                    ],
                    'SampleTime': '2023-05-12T12:00:00Z'
                }
            ]
        )
        return response
    except Exception as e:
        print(f"An error occurred while starting tracking: {e}")
        return None

def stop_tracking(tracker_name):
    try:
        client =  boto3.client('location',aws_access_key_id='AKIAVUQ3J33Z7NMO7M5S',
                        aws_secret_access_key='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', 
                              region_name='us-east-1')
        response = client.delete_tracker(
            TrackerName=tracker_name
        )
        return response
    except Exception as e:
        print(f"An error occurred while stopping tracking: {e}")
        return None



tracker_name = 'MyTracker'


def send_at(command,back,timeout):
	global FinalLat, FinalLong
	global GPSDATA
	rec_buff = ''
	ser.write((command+'\r\n').encode())
	time.sleep(timeout)
	if ser.inWaiting():
		time.sleep(0.01 )
		rec_buff = ser.read(ser.inWaiting())
	try:
		if rec_buff != '':
			if back not in rec_buff.decode():
				print(command + ' ERROR')
				print(command + ' back:\t' + rec_buff.decode())
				return 0
			else:
				
				GPSDATA = str(rec_buff.decode())
				print("Received GPS data:", GPSDATA)
				
				#print(rec_buff.decode())
				
				#Additions to Demo Code Written by Tim!
				
				#print(GPSDATA)
				Cleaned = GPSDATA[13:]
				#print("Cleaned GPS data:", Cleaned)
				
				#print(Cleaned)
				
				Lat = Cleaned[:2]
				SmallLat = Cleaned[2:11]
				NorthOrSouth = Cleaned[12]
				
				#print(Lat, SmallLat, NorthOrSouth)
				
				Long = Cleaned[14:17]
				SmallLong = Cleaned[17:26]
				EastOrWest = Cleaned[27]
				
				#print(Long, SmallLong, EastOrWest)   
				FinalLat = float(Lat) + (float(SmallLat)/60)
				FinalLong = float(Long) + (float(SmallLong)/60)
				
				if NorthOrSouth == 'S': FinalLat = -FinalLat
				if EastOrWest == 'W': FinalLong = -FinalLong
				
				print(FinalLat, FinalLong)
				start_tracking(tracker_name, device_id, FinalLat, FinalLong)  # Llamada a start_tracking con los datos obtenidos
				
				#print(FinalLat, FinalLong)
				#print(rec_buff.decode())
				
				return 1
		else:
			print('GPS is not ready')
			return 0
	except IndexError as e:
    		print("IndexError occurred:", e)

def get_gps_position():
	rec_null = True
	answer = 0
	print('Start GPS session...')
	rec_buff = ''
	send_at('AT+CGPS=1,1','OK',1)
	time.sleep(2)
	while rec_null:
		answer = send_at('AT+CGPSINFO','+CGPSINFO: ',1)
		if 1 == answer:
			answer = 0
			if ',,,,,,' in rec_buff:
				print('GPS is not ready')
				rec_null = False
				time.sleep(1)
		else:
			print('Error: {}'.format(answer))
			rec_buff = ''
			send_at('AT+CGPS=0','OK',1)
			return False
		time.sleep(1.5)


def power_on(power_key):
	print('SIM7600X is starting:')
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(power_key,GPIO.OUT)
	time.sleep(0.1)
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(2)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(20)
	ser.flushInput()
	print('SIM7600X is ready')

def power_down(power_key):
	print('SIM7600X is loging off:')
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(3)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(18)
	print('Good bye')

#Additions to Demo GPS.py Code Added by Tim // Simplfing the GPS Start up process
if __name__ == '__main__':
    power_on(power_key)
    #create_tracker(tracker_name)
    while True:
        get_gps_position()
      