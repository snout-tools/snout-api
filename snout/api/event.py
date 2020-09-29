from logging import StreamHandler


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
