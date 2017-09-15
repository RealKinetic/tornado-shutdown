# tornado-shutdown

Gracefully handling shutdown for server processes can be complicated. This
module attempts simplify things by handling SIGINT and SIGTERM for you. All you
need to do is add callbacks that are run when those signals are fired.

An example::
    from tornado import web
    from tornado import ioloop

    import tornado_shutdown as shutdown


    class MainHandler(web.RequestHandler):
        def get(self):
            self.write("Hello, world")


    application = web.Application([
        (r"/", MainHandler),
    ])

    if __name__ == '__main__':
        shutdown.install_handlers()

        server = application.listen(8888)

        shutdown.at_shutdown(server.stop)

        ioloop.start()

Run the above code and then issue a kill command in a separate terminal. E.g.:

    ``kill -2 PROCESS_ID`` or ``kill -15 PROCESS_ID``

This module is meant to be used as a singleton. In order to control the
shutdown deadline, ``TORNADO_SHUTDOWN_DEADLINE`` as an environment variable is
respected.

## Testing

Run ``python -m tornado_shutdown``

Will run an http server on 8888. Kill the process with ``kill -2`` or ``kill
-15`` and done. :)
