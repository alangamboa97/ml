
import cv2
import numpy as np
import boto3
import dlib
import json
import uuid
import geocoder
#from requests_aws4auth import AWS4Auth
#import requests
from imutils import face_utils
from cv2 import VideoWriter, VideoWriter_fourcc
from datetime import datetime
from decimal import Decimal
from scipy.spatial import distance as dist
import os
import dlib
import time
from alarma import activar_buzzer
import Jetson.GPIO as GPIO
#import gps

# from tracker import start_tracking
# from GPS import get_gps_position



#---------------------------------------Incidencia (video y coordenadas)------------------------------------------------------#

#credenciales

GPIO.setmode(GPIO.BOARD)    


dynamodb = boto3.resource('dynamodb',aws_access_key_id='AKIAVUQ3J33Z7NMO7M5S',
                        aws_secret_access_key='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', 
                              region_name='us-east-1')
table = dynamodb.Table('Incidencia-trjjwxbd3bbjrjauppwd23ijpi-dev')
conductores = dynamodb.Table('Conductor-trjjwxbd3bbjrjauppwd23ijpi-dev')


# Uso del método

video_count = 0
start_recording = 0
recording_duration = 5  # Duración de la grabación en segundos


#variables

location = geocoder.ip('me')

print(location.latlng)
try:
    coordenadas = json.loads(json.dumps(location.latlng), parse_float=Decimal)
    
    #coordenadas = gps.get_gps_position()
except:
    print("Error al obtener coordenadas")

try:
    conductor = conductores.get_item(
        TableName='Conductor-trjjwxbd3bbjrjauppwd23ijpi-dev',
        Key ={
            'id': '001'
        }
    )
except NameError as e:
    print('Error al obtener datos del conductor', e)

fecha_actual = str(datetime.now().date().today())
fecha_hora_actual = datetime.now()
hora_legible = fecha_hora_actual.strftime("%H:%M:%S")
#conductorId = conductor['Item']
id = str(uuid.uuid1())
power_key = 6
rec_buff = ''
rec_buff2 = ''
contador = 0
fourcc = cv2.VideoWriter_fourcc(*'H264')
video = None
conductorId = conductor['Item']
print(conductorId['nombre'])
somnolence_detected = False 





#---------------------------------------Deteccion de somnolencia------------------------------------------------------#

# Inicializar la cámara y tomar la instancia
gst_str = ('nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)NV12, framerate=(fraction)5/1 ! '
               'nvvidconv flip-method=2 ! video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx ! '
               'videoconvert ! video/x-raw, format=(string)BGR ! appsink')
cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

# Inicialización del detector de rostros y el detector de puntos de referencia
#-------Modelos---------#
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

#status marking for current state
sleep = 0
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)

def upload_video(file, url_video):

    
    
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
                    'ubicacion': coordenadas, 	
                    'createdAt': datetime.now().isoformat(timespec='milliseconds') +'Z',
                    'updatedAt': datetime.now().isoformat(timespec='milliseconds') +'Z',
                    '__typename': 'Incidencia',
                    

                    
                },
                    )
    print("Incidencia registrada")
    try:
            #start_media_convert_job(bucket, file, bucket_output, file_output)
        print("Job started")    
    except:
        print("Error al convertir archivo")

    print('Video subido... ', url_video)

def cal_yawn(landmarks):
	top_lip = landmarks[50:53]
	top_lip = np.concatenate((top_lip, landmarks[61:64]))

	low_lip = landmarks[56:59]
	low_lip = np.concatenate((low_lip, landmarks[65:68]))

	top_mean = np.mean(top_lip, axis=0)
	low_mean = np.mean(low_lip, axis=0)

	distance = dist.euclidean(top_mean,low_mean)
	return distance

def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist


def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up/(2.0*down)

    # Comprobando si parpadea
    if (ratio > 0.25): # parpadeo rapido 
        return 2
    elif (ratio > 0.21 and ratio <= 0.25): # Parpadeo Nnormal 
        return 1
    else:
        return 0 #no hay parpadeo 

#----------------------------Variables------------#
yawn_thresh = 45
ptime = 0
yawn_count = 0  # Contador de bostezos
start_time = time.time()  # Tiempo de inicio para el conteo
yawn_duration = 0  # Duración del bostezo actual
is_yawning = False  # Indicador de si se está produciendo un bostezo

#gps.power_on(power_key)
while True:
    id = str(uuid.uuid1())
    suc,frame = cap.read()
    
    if not suc :
        break

    #gps.get_gps_position()
    #---------FPS------------#	
    ctime = time.time()
    fps= int(1/(ctime-ptime))
    ptime = ctime
    cv2.putText(frame,f'FPS:{fps}',(frame.shape[1]-120,frame.shape[0]-20),cv2.FONT_HERSHEY_PLAIN,2,(0,200,0),3)

	
	#------Deteccion de rostro------#
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    # Detectar cara en matriz de caras
    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()

        face_frame = frame.copy()
        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        #----------------------------Detectar Landmarks--------#
        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        #--------------------------------Boca--------------------------#
        #-----------Detectar/Marcar puntos de referencia del labio superior e inferior-------#
        lip = landmarks[48:60]
        cv2.drawContours(frame,[lip],-1,(0, 165, 255),thickness=3)


        #--------------------------------OJOS--------------------------#
        # ----------Detectar/Marcar puntos de referencia que mostrarán a los ojos------------#
        left_blink = blinked(landmarks[36], landmarks[37],
                             landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43],
                              landmarks[44], landmarks[47], landmarks[46], landmarks[45])

        
        #----------------Cálculo de la distancia entre labios------------#
        lip_dist = cal_yawn(landmarks)
        #print(lip_dist)

        if lip_dist > yawn_thresh :
            print("Limite superado, valor: " + str(lip_dist))
            if not is_yawning:
                is_yawning = True
                start_time_yawn = time.time()  # Tiempo de inicio del bostezo
        else:
            if is_yawning:
                is_yawning = False
                end_time_yawn = time.time()  # Tiempo de finalización del bostezo
                yawn_duration = end_time_yawn - start_time_yawn
                print("Duración del bostezo:", yawn_duration, "segundos")

        #------------- parpadeos de los ojos----------#
        if (left_blink == 0 or right_blink == 0): 
            sleep += 1
            drowsy = 0
            active = 0
            
            if (sleep > 4):
                id += str(contador + 1)

                file = 'PRUEBA' + id  + '.mp4'
                url_video = 'https://d3gh7t05x84ron.cloudfront.net/'+ file
                status = "Dormido"
                color = (255,0,0)
                
                if video is None:
                       
                        video = cv2.VideoWriter(file, fourcc, 6, (640, 480))
                if video is not None:
                    video.write(frame)
                
                if not somnolence_detected:
                    
                    somnolence_detected = True
                    print('Valor somnolence ', somnolence_detected)
                    print("¡,,,,ALERTA! Se ha detectado somnolencia.")
                    activar_buzzer(2)
                    #activa
                   
                   
               
                            
                
        elif (left_blink == 1 or right_blink == 1): 
            sleep = 0
            active = 0
            drowsy += 1
            if (drowsy > 4):
                id += str(contador + 1)
                file = 'PRUEBA' + id  + '.mp4'
                url_video = 'https://d3gh7t05x84ron.cloudfront.net/'+ file
                status = "Somnoliento"
                color = (0, 0, 255)
                
                if video is None:
                        
                        video = cv2.VideoWriter(file, fourcc, 6, (640, 480))
                if video is not None:
                    video.write(frame)
              
                
                if not somnolence_detected:
                   
                    somnolence_detected = True
                    print('Valor somnolence ', somnolence_detected)
                    print("¡ALERTA! Se ha detectado somnolencia.")
                    activar_buzzer(2)
                    #video.release()
                    #upload_video(file)
                    
                
         
        else:
            drowsy = 0
            sleep = 0
            active += 1
            if (active > 6):
                status = "Activo"
                color = (0, 255, 0)
               
                    
                if somnolence_detected:
                    somnolence_detected = False
                    video.release()
                    #upload_video(file, url_video)



        cv2.putText(frame, status, (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color,3) #Escribir texto en la imagen
    
        current_time = time.time()
        elapsed_time = current_time - start_time
        #print(elapsed_time)

        #----------------------------Deteccion de bostezos por minuto----------------------#
        if elapsed_time >= 60:  # Si ha pasado 1 minuto 
                yawn_count = 0  # Reiniciar el contador de bostezos
                start_time = current_time  # Reiniciar el tiempo de inicio

        if elapsed_time < 60: # Si se detectan mas de 2 bostezos envia alerta
            if yawn_count >= 2:
                print("¡ALERTA! Se han detectado más de 2 bostezos por minuto.")

                #grabar video
                #video.write(frame)

                #upload_video(file)

        #----------------------------Conteo de Bostezos----------------------#
        if yawn_duration >= 4:  # Si la duración del bostezo es igual o mayor a 5 segundos se considera bostezo
            yawn_count += 1
            status = "Bostezo !!!"
            #activar_buzzer(3)
            print('ALERTA')
            color = (255, 255, 0)
            yawn_duration = 0  # Reiniciar la duración del bostezo
   
        #  iterar sobre los 68 landmarks detectados en el rostro y dibujar un círculo en cada uno de ellos.
        for n in range(0, 68):  
            (x, y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)
    
     
    cv2.imshow('CSI camera' , frame) # mostrar imagen en una ventana.
    
    if video is not None:
        video.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Tecla 'q' presionada. Finalizando el programa...")
        if video is not None:
            video.release()
            
        if cap is not None:
            cap.release()
            
        cv2.destroyAllWindows()
      

# Liberar recursos y cerrar ventanas
if video is not None:
    video.release()
if cap is not None:
    cap.release()
cv2.destroyAllWindows()
