import multiprocessing
from Somnolencia import detectar_somnolencia
from GPS import obtener_localizacion_gps
from Incidencias import crear_incidencia

if __name__ == '__main__':
    # Iniciar los procesos para cada script en paralelo
    somnolencia_process = multiprocessing.Process(target=detectar_somnolencia)
    gps_process = multiprocessing.Process(target=obtener_localizacion_gps)
    incidencias_process = multiprocessing.Process(target=crear_incidencia)

    # Iniciar los procesos
    somnolencia_process.start()
    gps_process.start()
    incidencias_process.start()

    try:
        # Mantener los procesos en funcionamiento indefinidamente
        while True:
            pass

    except KeyboardInterrupt:
        # Manejar una interrupción del teclado (Ctrl+C) para detener el programa
        somnolencia_process.terminate()
        gps_process.terminate()
        incidencias_process.terminate()
        somnolencia_process.join()
        gps_process.join()
        incidencias_process.join()

