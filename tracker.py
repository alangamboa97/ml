import boto3
import json

from geopy.geocoders import Nominatim
client =  boto3.client('location',aws_access_key_id='AKIAVUQ3J33Z7NMO7M5S',
                        aws_secret_access_key='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', 
                              region_name='us-east-1')


def create_tracker(tracker_name):
    client = boto3.client('location')
    response = client.create_tracker(
        TrackerName=tracker_name,
        Description='My Tracker'
    )
    print("Tracker created successfully!")
    return response

def get_current_location():
    geolocator = Nominatim(user_agent="me")
    location = geolocator.geocode(query='', exactly_one=True, timeout=10)
    if location:
        return location.latitude, location.longitude
    else:
        return None


def start_tracking(tracker_name, device_id, latitude, longitude):
    response = client.batch_update_device_position(
        TrackerName=tracker_name,
        Updates=[
            {
                'DeviceId': device_id,
                'Position': [
                    longitude,  # longitude
                    latitude  # latitude
                ],
                'SampleTime': '2023-05-12T12:00:00Z'
            }
        ]
    )
    return response


def stop_tracking(tracker_name):
    response = client.delete_tracker(
        TrackerName=tracker_name
    )
    return response


tracker_name = 'MyTracker'

coordinates = get_current_location()

if coordinates:
    latitude, longitude = coordinates
    print("Latitude:", latitude)
    print("Longitude:", longitude)
else:
    print("Ubicación en tiempo real no disponible.")


device_id = 'MyDevice'
#create_tracker(tracker_name)
#start_tracking(tracker_name, device_id, coordinates[latitude], coordinates[longitude])
#stop_tracking(tracker_name)
print('Rastreo iniciado')


# Aquí puedes agregar código adicional para actualizar y obtener ubicaciones del rastreador


