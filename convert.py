import requests

def convertir_avi_a_mp4(api_key, input_file_path, output_file_path):
    # Configura la URL de la API de CloudConvert
    api_url = "https://api.cloudconvert.com/v2/convert"
    
    # Configura las cabeceras con la clave de API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    # Configura el cuerpo de la solicitud con los detalles de la conversión
    data = {
        "inputformat": "avi",
        "outputformat": "mp4",
        "input": "upload",
        "file": open(input_file_path, "rb"),
    }

    # Realiza la solicitud POST a la API de CloudConvert
    response = requests.post(api_url, headers=headers, files=data)

    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        # Guarda el archivo convertido
        with open(output_file_path, "wb") as output_file:
            output_file.write(response.content)
        print("Conversión exitosa")
    else:
        print(f"Error en la conversión: {response.status_code}, {response.text}")

# Ejemplo de uso




