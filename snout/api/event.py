import threading
from logging import StreamHandler
import umsgpack
import zmq


class EventSystem(object):
    addr = 'ipc:///tmp/snout.eventsystem.z'
    _ctx = None
    _sock = None

    @classmethod
    def _ensurecontext(cls):
        if not cls._ctx and not cls._sock:
            cls._ctx = zmq.Context()
            cls._sock = cls._ctx.socket(zmq.PUB)
            cls._sock.bind(cls.addr)

    @classmethod
    def emit(cls, channel, message):
        cls._ensurecontext()
        cls._sock.send_multipart([channel.encode('utf-8'), umsgpack.packb(message)])


class EventListener(object):
    def __init__(self, handlers=None, start=False):
        self._context = zmq.Context()
        self._sock = self._context.socket(zmq.SUB)
        self._sock.connect(EventSystem.addr)
        self._stop = threading.Event()
        self._listener = None
        self.handlers = {}
        if isinstance(handlers, dict):
            for k, v in handlers.items():
                if callable(v):
                    self.handlers[k] = v
                    self._sock.setsockopt_string(zmq.SUBSCRIBE, k)
                else:
                    raise TypeError(f'Provided event handler {v} is not callable.')

    def start(self):
        self._listener = threading.Thread(target=self._listener_loop, daemon=True)
        self._listener.start()

    def _listener_loop(self):
        while not self._stop.is_set():
            self.listen()

    def listen(self):
        rec = self._sock.recv_multipart()
        if not self._stop.is_set():
            handler = rec[0].decode('utf-8')
            msg = umsgpack.unpackb(rec[1])
            self.handlers[handler](msg)

    def stop(self):
        self._stop.set()


class EventMgmtCapability(object):
    """Event notification capability.

    Objects inheriting from this class will be able to emit events, and to
    subscribe to events by registering event handlers.
    """

    _handlers = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def registerEventHandler(self, name, handler):
        self.__class__._handlers.setdefault(name, set()).add(handler)

    def deregisterEventHandler(self, name, handler):
        if name in self.__class__._handlers and handler in self.__class__._handlers[name]:
            self.__class__._handlers[name].remove(handler)

    def emitEvent(self, notification):
        handlers = set()
        # Consider handlers for this notification
        handlers.update(self.__class__._handlers.get(notification.name, set()))
        # Consider catch-all handlers for this event type
        topevent = notification.name.split('.')[0]
        handlers.update(self.__class__._handlers.get(topevent, set()))
        for handler in handlers:
            handler(*notification.args, **notification.kwargs)
        return True

    def eventName(self, proto, event):
        return '%s.%s' % (str(proto).strip().lower(), str(event).strip().lower())


class Notification(object):
    """The Notification class used for the :class: EventMgmtCapability."""

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs


class SnoutEventHandler(StreamHandler, EventMgmtCapability):
    def __init__(self, eventname='log'):
        super().__init__()
        self.eventname = eventname

    def emit(self, record):
        msg = self.format(record)
        self.emitEvent(Notification(self.eventname, msg))
