import time

import eventlet
import flask
import flask_socketio

import dog_game

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# TODO: Does not work
'''
https://medium.com/hackervalleystudio/weekend-project-part-1-creating-a-real-time-web-based-application-using-flask-vue-and-socket-b71c73f37df7
https://medium.com/hackervalleystudio/weekend-project-part-2-turning-flask-into-a-real-time-websocket-server-using-flask-socketio-ab6b45f1d896
https://medium.com/hackervalleystudio/weekend-project-part-3-centralizing-state-management-with-vuex-5f4387ebc144
'''
params = dict(
	# ping_timeout=1000,
	# ping_interval=5000,
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=False,
    async_mode='eventlet'
    # async_mode='threading'
)
# socketio = flask_socketio.SocketIO(app, ping_timeout=20, ping_interval=10)
socketio = flask_socketio.SocketIO(app, **params)

game = dog_game.Game()

@socketio.on('message')
def handleMessage(msg):
    print(f'Message: {msg}\n')
    socketio.send(f'MESSAGE:{msg}', broadcast=True)

@socketio.on('event')
def handleEvent(json):
    print(f'Json: {json}\n')
    game.event(json)

@socketio.on('move')
def handleMove(json):
    print(f'Json: {json}\n')
    # socketio.send(dict(dx=json['dx'], dy=json['dy']), json=True)
    json_command = [
        {
            "svg_id": "#svg .colorchange",
            "transform":  json['transform']
        },
    ]
    socketio.send(json_command, json=True, broadcast=True)

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
        socketio.send(data_json, json=True, broadcast=True)
        return 'Yes'
    return 'No'

    # curl -X POST http://localhost:5000/debugjson -d @set_all_1.json 

def timer_run():
    while True:
        str_time = time.strftime('%H:%M:%S')
        data_json = {
            "call_html": {
                "id": "#time",
                "calls": {
                    "html": str_time
                }
            }
        }
        socketio.send(data_json, json=True, broadcast=True)
        eventlet.sleep(1.0)

if __name__ == '__main__':
    # eventlet.spawn(timer_run)

    socketio.run(app, host="0.0.0.0")
