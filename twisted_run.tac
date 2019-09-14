from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.web import server
from __init__ import app as application

resource = WSGIResource(reactor, reactor.getThreadPool(), application)
site = server.Site(resource)
reactor.listenTCP(8080, site)
reactor.run()