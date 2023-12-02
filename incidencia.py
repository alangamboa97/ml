
import cv2

import time
import requests
import boto3
import os

import uuid
from datetime import datetime
#import moviepy.editor as moviepy
import geocoder
import json
from decimal import Decimal

#credenciales
class Incidencia: 
    dynamodb = boto3.resource('dynamodb',aws_access_key_id='AKIAVUQ3J33Z7NMO7M5S',
                            aws_secret_access_key='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', 
                                region_name='us-east-1')
    table = dynamodb.Table('Incidencia-trjjwxbd3bbjrjauppwd23ijpi-dev')
    conductores = dynamodb.Table('Conductor-trjjwxbd3bbjrjauppwd23ijpi-dev')


    location = geocoder.ip('me')
    print(location.latlng)
    coordenadas = json.loads(json.dumps(location.latlng), parse_float=Decimal)

    id = str(uuid.uuid1())
    url_video = 'https://d3gh7t05x84ron.cloudfront.net/'+ id +'.mp4'



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



    ptime = 0




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
                'conductorIncidenciasId': conductorId['id'],
                'fecha': fecha_actual,
                'hora': hora_legible,
                'createdAt': datetime.now().isoformat(timespec='milliseconds') +'Z',
                'updatedAt': datetime.now().isoformat(timespec='milliseconds') +'Z',
                '__typename': 'Incidencia',
                

                
            },
                )

    #print(fecha_actual)
    #cam.release()
    #video.release()
    #clip = moviepy.VideoFileClip(file)
    #clip.write_videofile(id + '.mp4')

    #cv2.destroyAllWindows()
    upload_video(id+'.mp4')

