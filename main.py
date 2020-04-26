import flask
import flask_socketio

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = flask_socketio.SocketIO(app)

@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	socketio.send(msg, broadcast=True)

@app.route('/')
def index():
    return flask.render_template('index.html')

if __name__ == '__main__':
	socketio.run(app)
