import os
import json
import socketio


def sio_send(event, data_string, data_file):
    if data_file and os.path.isfile(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
    else:
        data = json.loads(data_string)

    sio = socketio.Client()
    sio.connect('http://localhost:8888')

    def callback(resp):
        print('=' * 32)
        print('Response:')
        print(json.dumps(resp, indent=2))
        sio.disconnect()

    print('Send Request:')
    print(json.dumps(data, indent=2))
    sio.emit(event, data=data, callback=callback)
