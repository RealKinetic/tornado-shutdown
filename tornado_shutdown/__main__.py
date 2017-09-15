#!/usr/bin/env python

from tornado import ioloop
from tornado import web
from tornado import httpserver

import tornado_shutdown as shutdown


class MainHandler(web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def main():
    application = web.Application([
        (r"/", MainHandler),
    ])

    server = httpserver.HTTPServer(application)
    server.listen(8888)

    shutdown.install_handlers()

    shutdown.at_shutdown(server.stop)

    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
