import dlib
import cv2
import time

# Inicializa el detector de puntos faciales de dlib
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Inicializar la cámara
gst_str = ('nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)NV12, framerate=(fraction)5/1 ! '
               'nvvidconv flip-method=2 ! video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx ! '
               'videoconvert ! video/x-raw, format=(string)BGR ! appsink')
cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

# Variables para el contador de tiempo de ojos cerrados
contador = 0
tiempo_inicio = 0

while True:
    ret, frame = cap.read()

    # Convierte la imagen a escala de grises para un mejor rendimiento
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detecta caras en la imagen
    faces = detector(gray)

    for face in faces:
        # Detecta los puntos faciales
        landmarks = predictor(gray, face)
        left_eye_ratio = (landmarks.part(42).y - landmarks.part(38).y) / (landmarks.part(41).x - landmarks.part(37).x)
        right_eye_ratio = (landmarks.part(47).y - landmarks.part(43).y) / (landmarks.part(46).x - landmarks.part(42).x)

        # Si el cociente de los ojos es menor que un umbral, consideramos que los ojos están cerrados
        if left_eye_ratio < 0.2 and right_eye_ratio < 0.2:
            if tiempo_inicio == 0:
                tiempo_inicio = time.time()
            contador = time.time() - tiempo_inicio
        else:
            tiempo_inicio = 0
            contador = 0

    # Muestra el contador en la ventana de la cámara
    cv2.putText(frame, f"Tiempo ojos cerrados: {contador:.2f} segundos", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Muestra la imagen en tiempo real
    cv2.imshow("Detección de ojos", frame)

    # Sale del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

