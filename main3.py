import cv2
import numpy as np
import boto3
import dlib
import subprocess
import ffmpeg
import json
import uuid
import geocoder
#from requests_aws4auth import AWS4Auth
import requests
from imutils import face_utils
from cv2 import VideoWriter, VideoWriter_fourcc
from datetime import datetime
from decimal import Decimal
import os
from media_convert import start_media_convert_job


#credenciales

dynamodb = boto3.resource('dynamodb',aws_access_key_id='AKIAVUQ3J33Z7NMO7M5S',
                        aws_secret_access_key='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', 
                              region_name='us-east-1')
table = dynamodb.Table('Incidencia-trjjwxbd3bbjrjauppwd23ijpi-dev')
conductores = dynamodb.Table('Conductor-trjjwxbd3bbjrjauppwd23ijpi-dev')


# Uso del método
input_file = 'prueba.avi'
output_file = 'video.mp4'


#variables

#location = geocoder.ip('me')
#print(location.latlng)
coordenadas = 2



conductor = conductores.get_item(
	TableName='Conductor-trjjwxbd3bbjrjauppwd23ijpi-dev',
	Key ={
		'id': '001'
	}
)

fecha_actual = str(datetime.now().date().today())
fecha_hora_actual = datetime.now()
hora_legible = fecha_hora_actual.strftime("%H:%M:%S")
conductorId = conductor['Item']
id = str(uuid.uuid1())
power_key = 6
rec_buff = ''
rec_buff2 = ''
time_count = 0
file = 'DIC' + id  + '.mp4'
fourcc = cv2.VideoWriter_fourcc(*'H264')
video = None
conductorId = conductor['Item']
print(conductorId['nombre'])
bucket_output = 'alan-video-output'

url_video = 'https://d3gh7t05x84ron.cloudfront.net/'+ file


#Initializing the camera and taking the instance

gst_str = ('nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)NV12, framerate=(fraction)6/1 ! '
               'nvvidconv flip-method=0 ! video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx ! '
               'videoconvert ! video/x-raw, format=(string)BGR ! appsink')
cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

#Initializing the face detector and landmark detector
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

#status marking for current state
sleep = 0
drowsy = 0
active = 0
status=""
color=(0,0,0)


def upload_video(file):
    
    client = boto3.client('s3', 
                        aws_access_key_id='AKIAVUQ3J33Z7NMO7M5S',
                        aws_secret_access_key='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',
                        region_name='us-east-1')
    
    

    bucket = 'videos175126-dev'
    cur_path = os.getcwd()
		
    filename = os.path.join(cur_path,file)
    

    	#abrir archivo
    data = open(filename, 'rb')

    #subir archivo
    client.upload_file(filename, bucket, file)
    table.put_item(
        Item={
            'id': id,
            'estado': None,
	    	'url_video': url_video,
		    'conductorIncidenciasId': conductorId['id'],
		    'fecha': fecha_actual,
		    'hora': hora_legible,
	    	'createdAt': datetime.now().isoformat(timespec='milliseconds') +'Z',
		    'updatedAt': datetime.now().isoformat(timespec='milliseconds') +'Z',
		    '__typename': 'Incidencia',
		    

            
        },
            )
    #convertir el archivo avi a mp4 mediante mediaconvert
    try:
        response = start_media_convert_job(bucket, file,)
    except:
         print("Error al convertir archivo")


def compute(ptA,ptB):
	dist = np.linalg.norm(ptA - ptB)
	return dist

def blinked(a,b,c,d,e,f):
	up = compute(b,d) + compute(c,e)
	down = compute(a,f)
	ratio = up/(2.0*down)

	#Checking if it is blinked
	if(ratio>0.25):
		return 2
	elif(ratio>0.21 and ratio<=0.25):
		return 1
	else:
		return 0

#gps.power_on(power_key)
while True:
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    #gps.get_gps_position()
    faces = detector(gray)
    #detected face in faces array
    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()

        face_frame = frame.copy()
        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        #The numbers are actually the landmarks which will show eye
        left_blink = blinked(landmarks[36],landmarks[37], landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42],landmarks[43], landmarks[44], landmarks[47], landmarks[46], landmarks[45])
        
        #Now judge what to do for the eye blinks
        if left_blink==0 or right_blink==0 :
            sleep+=1
            drowsy=0
            active=0
		
            if sleep>4 :
                status="SOMNOLENCIA!!!"
                color = (255,0,0)

                if video is None:
                    video = cv2.VideoWriter(file, fourcc, 6, (640, 480))
                video.write(frame)
                upload_video(file)
  
			

        elif left_blink==1 or right_blink==1 :
            sleep=0
            active=0		
            drowsy+=1
            if(drowsy>6):
                status="Drowsy!"
                color = (0,0,255)
                

        else:
            drowsy=0
            sleep=0
            active+=1
            if(active>6):
                status="Activo"
                color = (0,255,0)

        cv2.putText(frame, status, (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color,3)

        for n in range(0, 68):
            (x,y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)
    if key == 27:
      	break
    
if video is not None:
    video.release()

