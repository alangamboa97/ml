import numpy as np
import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
import dlib
import time
import requests
#from requests_aws4auth import AWS4Auth
import boto3
import os
from scipy.spatial import distance as dist
from imutils import face_utils
import uuid
from datetime import datetime
#import moviepy.editor as moviepy
import geocoder
import json
from decimal import Decimal


def cal_yawn(shape):
	top_lip = shape[50:53]
	top_lip = np.concatenate((top_lip, shape[61:64]))

	low_lip = shape[56:59]
	low_lip = np.concatenate((low_lip, shape[65:68]))

	top_mean = np.mean(top_lip, axis=0)
	low_mean = np.mean(low_lip, axis=0)

	distance = dist.euclidean(top_mean,low_mean)
	return distance



#--------Variables-------#
yawn_thresh = 25
ptime = 0




while True :
	suc,frame = cam.read()

	if not suc :
		break


	#---------FPS------------#	
	ctime = time.time()
	fps= int(1/(ctime-ptime))
	ptime = ctime
	cv2.putText(frame,f'FPS:{fps}',(frame.shape[1]-120,frame.shape[0]-20),cv2.FONT_HERSHEY_PLAIN,2,(0,200,0),3)

	

	#------Detecting face------#
	img_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	faces = face_model(img_gray)
	for face in faces:
		# #------Uncomment the following lines if you also want to detect the face ----------#
		#x1 = face.left()
		#y1 = face.top()
		#x2 = face.right()
		#y2 = face.bottom()
		#print(face.top())
		#cv2.rectangle(frame,(x1,y1),(x2,y2),(200,0,00),2)


		#----------Detect Landmarks-----------#
		shapes = landmark_model(img_gray,face)
		shape = face_utils.shape_to_np(shapes)

		#-------Detecting/Marking the lower and upper lip--------#
		lip = shape[48:60]
		cv2.drawContours(frame,[lip],-1,(0, 165, 255),thickness=3)

		#-------Calculating the lip distance-----#
		lip_dist = cal_yawn(shape)
		# print(lip_dist)
		if lip_dist > yawn_thresh :
			#grabar video
			print('Bostezo detectado')
			video.write(frame)
			cv2.putText(frame, f'Limite superado',(frame.shape[1]//2 - 170 ,frame.shape[0]//2),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,200),2)
			

	cv2.imshow('CSI camera' , frame)
	if cv2.waitKey(1) & 0xFF == ord('q') :
		break


#subir video

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
		    'ubicacion': coordenadas,
	    	'createdAt': datetime.now().isoformat(timespec='milliseconds') +'Z',
		    'updatedAt': datetime.now().isoformat(timespec='milliseconds') +'Z',
		    '__typename': 'Incidencia',
		    

            
        },
            )
    

cam.release()
video.release()
#clip = moviepy.VideoFileClip(file)
#clip.write_videofile(id + '.mp4')

cv2.destroyAllWindows()
upload_video(id+'.mp4')
