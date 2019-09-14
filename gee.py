from gevent.wsgi import WSGIServer
from __init__ import *
from model import product


http_server = WSGIServer(('', 8080), app)
http_server.serve_forever()