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
