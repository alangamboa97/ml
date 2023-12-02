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



#credenciales
def sign_in():
	dynamodb = boto3.resource('dynamodb',aws_access_key_id='AKIAVUQ3J33Z7NMO7M5S',
	                        aws_secret_access_key='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', 
                              region_name='us-east-1')
	table = dynamodb.Table('Incidencia-trjjwxbd3bbjrjauppwd23ijpi-dev')



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


#clip = moviepy.VideoFileClip(file)
#clip.write_videofile(id + '.mp4')


