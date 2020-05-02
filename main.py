import time
import threading

import flask
import flask_socketio

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = flask_socketio.SocketIO(app)

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
