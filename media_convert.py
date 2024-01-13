import boto3


def start_media_convert_job(input_bucket, input_key, output_bucket, output_key):

    # Reemplaza 'tu_region' con la región AWS adecuada
    try:
        mediaconvert_client = boto3.client('mediaconvert',aws_access_key_id='AKIAVUQ3J33Z7NMO7M5S',
                            aws_secret_access_key='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', 
                                region_name='us-east-1',endpoint_url='https://lxlxpswfb.mediaconvert.us-east-1.amazonaws.com')
    except Exception as e:
        print(e, 'Error creating mediaconvert client')
        raise e

    try:
        job_settings = {
            "Queue": "Default",  # Reemplaza 'tu_cola_de_trabajo' con el nombre de tu cola MediaConvert
            "UserMetadata": {},
            "Role": 'arn:aws:iam::387678068467:user/admin',  # Reemplaza 'tu_arn_de_rol' con el ARN de tu rol de MediaConvert
            "Settings": {
                "Inputs": [
                    {
                        "FileInput": f"s3://{input_bucket}/{input_key}"
                    }
                ],
                "OutputGroups": [
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
        }


        response = mediaconvert_client.create_job(**job_settings)
    except Exception as e:
        print(e, 'Error creating mediaconvert job')
        raise e
    return response
