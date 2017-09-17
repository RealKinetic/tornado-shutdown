"""
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
shutdown deadline, `TORNADO_SHUTDOWN_DEADLINE` as an environment variable is
respected.

Heavily influenced by gists such as:
https://gist.github.com/wonderbeyond/d38cd85243befe863cdde54b84505784
"""

import os
import signal
import time

from tornado import ioloop
from tornado.log import gen_log as LOG


__all__ = [
    'install_handlers',
    'at_shutdown',
]

# maximum number of seconds to wait after receiving the SIGINT/SIGTERM signal
# to force the shutdown of the current ioloop.
SHUTDOWN_DEADLINE = 5


class TornadoShutdown(object):
    def __init__(self, max_wait=SHUTDOWN_DEADLINE, time_func=time.time):
        self.max_wait = max_wait
        self.time_func = time_func

        self.funcs = []
        self._handlers_installed = False
        self.shutting_down = False

    def at_shutdown(self, func):
        if not self._handlers_installed:
            raise EnvironmentError(
                'Call `install_handlers` before adding shutdown callbacks'
            )

        self.funcs.append(func)

    def install_handlers(self):
        if self._handlers_installed:
            return

        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

        self._handlers_installed = True

    def handle_signal(self, sig, frame):
        io_loop = ioloop.IOLoop.current()

        if self.shutting_down:
            # repeated signal - just kill the loop
            LOG.warn('Caught signal %d again, terminating ..', sig)
            io_loop.stop()

            return

        self.shutting_down = True

        LOG.warn('Caught signal %d', sig)

        io_loop.add_callback_from_signal(self.shutdown, io_loop)

    def shutdown(self, io_loop):
        for func in self.funcs[:]:
            try:
                func()
            except:
                LOG.exception('Failed to call %r', func)

        LOG.warn(
            'Shutdown initiated, will force stop in %d seconds',
            self.max_wait
        )
        self.stop_loop(io_loop, self.time_func() + self.max_wait)

    def stop_loop(self, io_loop, deadline):
        now = self.time_func()

        if now < deadline and self.is_loop_busy(io_loop):
            io_loop.call_later(0.5, self.stop_loop, io_loop, deadline)

            return

        if now >= deadline:
            LOG.warn('Deadline passed, forcing stop ..')

        io_loop.stop()
        LOG.warn('Shutdown complete')

    def is_loop_busy(self, io_loop):
        return (io_loop._callbacks or io_loop._timeouts)


_shutdown = TornadoShutdown(
    max_wait=int(os.getenv('TORNADO_SHUTDOWN_DEADLINE', SHUTDOWN_DEADLINE))
)

install_handlers = _shutdown.install_handlers
at_shutdown = _shutdown.at_shutdown
