import boto3


def start_media_convert_job(input_bucket, input_key, output_bucket, output_key):
    # Reemplaza 'tu_region' con la región AWS adecuada
    mediaconvert_client = boto3.client('mediaconvert', region_name='tu_region')

    job_settings = {
        "Input": {
            "FileInput": f"s3://{input_bucket}/{input_key}"
        },
        "OutputGroupSettings": [
            {
                "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {
                        "Destination": f"s3://{output_bucket}/{output_key}"
                    }
                },
                "Outputs": [
                    {
                        "ContainerSettings": {
                            "Container": "MP4",
                            "Mp4Settings": {}
                        }
                    }
                ]
            }
        ]
    }

    response = mediaconvert_client.create_job(
        Queue='Default',  # Reemplaza 'tu_cola_de_trabajo' con el nombre de tu cola MediaConvert
        UserMetadata={},
        # Reemplaza 'tu_arn_de_rol' con el ARN de tu rol de MediaConvert
        Role='arn:aws:iam::387678068467:role/MediaConverterRole',
        Settings=job_settings
    )

    return response


# Llamada a la función para iniciar la conversión
response = start_media_convert_job(
    'bucket_de_entrada', 'video.avi', 'bucket_de_salida', 'video.mp4')
print(response)
