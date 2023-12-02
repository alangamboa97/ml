
import Jetson.GPIO as GPIO
import time


BUZZER_PIN = 32  # Buzzer pin number
GPIO.setwarnings(False)

def play_sound(duration, frequency):  # Play different frequencies
    for i in range(duration):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(1/frequency)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(1/frequency)


GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

notes = {  # Diccionario de notas y frecuencias
    'C': 2000, 'A': 440, 'E': 659.25, 'F': 698.46, 'G': 783.99, 'H': 1100,
}

for n in ['C', 'H', 'C', 'H', 'C']:  # Play notas
    play_sound(300, notes[n])
        #time.sleep(0.1)

GPIO.cleanup() # Limpiar y liberar el puerto GPIO
