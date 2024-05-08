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


@sio.event
def get_client_id(data):
    print(data)


if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    sio.emit('message', 'Hello from client')
    sio.wait()
