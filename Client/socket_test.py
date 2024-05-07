import json

import requests
import socketio

sio = socketio.Client()
api_url = 'http://localhost:5000/api/v1/test-socket'
api_data = {'key': 'value'}
api_headers = {}



@sio.event
def message(data):
    print('ID socket phía server:', data)
    data_dict = json.loads(data)
    api_headers['socket_id'] = data_dict['Client ID']


if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    response = requests.get(api_url, params=api_data, headers=api_headers)
    if response.status_code == 200:
        print('Response:', response.json())
    else:
        print('Request thất bại:', response.status_code)
    sio.wait()

