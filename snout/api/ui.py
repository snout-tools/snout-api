from queue import Queue


class UI(object):
    def __init__(self, *args, **kwargs):
        self.app = kwargs.get('app', None)

        self.print_queues = {}
        pqueues = kwargs.get('print_queues', {})
        for name, queue in pqueues.items():
            if isinstance(queue, Queue):
                self.print_queues[name] = queue
        self.window = kwargs.get('window', None)

    def put(self, channel, value):
        if channel in self.print_queues.keys():
            self.print_queues[channel].put(value)
        else:
            if '_stdout' not in self.print_queues.keys():
                self.print_queues['_stdout'] = Queue()
            self.print_queues['_stdout'].put(value)
            # TODO: Should probably log a warning for this fallback
