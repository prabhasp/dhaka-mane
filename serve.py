from gevent import monkey; monkey.patch_all()
import gevent
import random
import serial

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
ser = serial.Serial('/dev/ttyUSB0', 19200, timeout=100)
 
class CPUNamespace(BaseNamespace, BroadcastMixin):
    def recv_connect(self):
	def send_ser():
		while 1:
			print "waiting..."
			x = ser.read()
			if len(x) > 0:
				print ord(x), x
				self.emit('key_data', ord(x))
			ser.flushInput()
			gevent.sleep(0.1)
	self.spawn(send_ser)

    def on_left(self):
        self.emit('key_data', 'B')
        print "LEFT"

    def on_right(self):
        self.emit('key_data', 'F')
        print "RIGHT"


class Application(object):
    def __init__(self):
        self.buffer = []

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/') or 'index.html'

        if path.startswith('static/') or path == 'index.html':
            try:
                data = open(path).read()
            except Exception:
                return not_found(start_response)

            if path.endswith(".js"):
                content_type = "text/javascript"
            elif path.endswith(".css"):
                content_type = "text/css"
            else:
                content_type = "text/html"

            start_response('200 OK', [('Content-Type', content_type)])
            return [data]

        if path.startswith("socket.io"):
            socketio_manage(environ, {'/cpu': CPUNamespace})
        else:
            return not_found(start_response)


def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']


if __name__ == '__main__':
    print 'Listening on port http://0.0.0.0:8080 and on port 10843 (flash policy server)'
    SocketIOServer(('0.0.0.0', 8080), Application(),
        resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 10843)).serve_forever()
