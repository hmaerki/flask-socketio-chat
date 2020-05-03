import time
import threading

import flask
import flask_socketio

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# TODO: Does not work
'''
https://medium.com/hackervalleystudio/weekend-project-part-1-creating-a-real-time-web-based-application-using-flask-vue-and-socket-b71c73f37df7
https://medium.com/hackervalleystudio/weekend-project-part-2-turning-flask-into-a-real-time-websocket-server-using-flask-socketio-ab6b45f1d896
https://medium.com/hackervalleystudio/weekend-project-part-3-centralizing-state-management-with-vuex-5f4387ebc144
'''
params = dict(
	ping_timeout=100,
	ping_interval=50,
    cors_allowed_origins='*',
    # async_mode='eventlet'
    async_mode='threading'
)
# socketio = flask_socketio.SocketIO(app, ping_timeout=20, ping_interval=10)
socketio = flask_socketio.SocketIO(app, **params)

@socketio.on('message')
def handleMessage(msg):
    print(f'Message: {msg}\n')
    socketio.send(f'MESSAGE:{msg}', broadcast=True)

@socketio.on('move')
def handleMove(json):
    print(f'Json: {json}\n')
    # socketio.send(dict(dx=json['dx'], dy=json['dy']), json=True)
    socketio.send(dict(transform=json['transform']), json=True)

@app.route('/')
def index():
    return flask.render_template('index.html')

# https://riptutorial.com/flask/example/5832/receiving-json-from-an-http-request
@app.route('/debugjson', methods=['POST', 'GET']) 
def debugjson():
    content_type = flask.request.headers['Content-Type']
    if content_type == 'application/x-www-form-urlencoded':
        data_json = flask.json.loads(flask.request.get_data().decode("utf-8"))
        print(f'debugjson: {data_json}\n')
        socketio.send(data_json, json=True)
        return 'Yes'
    return 'No'

    # curl -X POST -H 'Content-Type: application/json' http://localhost:5000/debugjson -d '{"name": "Alice"}' 

class Timer(threading.Thread):
    def __init__(self, socketio):
        threading.Thread.__init__(self)
        self.socketio = socketio

    def run(self):
        while True:
            time.sleep(1.0)
            msg = time.strftime('%H:%M:%S')
            socketio.send(f'TIME:{msg}')

if __name__ == '__main__':
    timer = Timer(socketio)
    timer.start()

    socketio.run(app)
