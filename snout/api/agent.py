import time
from enum import IntFlag

from snout.api.event import EventMgmtCapability
from snout.api.hier import AppHierarchy
from snout.api.log import Logger

Status = IntFlag('Status', 'Unknown Idle Starting Running Stopping Stopped Complete Failed')


class SnoutAgent(Logger, EventMgmtCapability, AppHierarchy):
    """SnoutAgent is the main base class providing basic common functionality.

    Args:
        name (str, optional): Nickname of the object.
        parent (SnoutAgent, optional): The parent object.

    Attributes:
        instances (list): Retains a list of active SnoutAgent instances.
    """

    instances = []

    __request_exit__ = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        SnoutAgent.instances.append(self)
        self.args = args
        self.kwargs = kwargs
        self._nickname = kwargs.get('name', None)
        self._app = kwargs.get('app', None)
        # State
        self._statuslog = []
        self._status = Status.Unknown

        # Runtime
        self.status = Status.Idle

    @classmethod
    def find_instance(cls, searchterm):
        return [i for i in SnoutAgent.instances if searchterm in i.name]

    @property
    def app(self):
        if self._app:
            return self._app
        if self.parent:
            return self.parent.app
        return None

    @property
    def name(self):
        """Hierarchical name of the SnoutAgent object.

        Returns:
            str: Hierarchical name of the SnoutAgent object.
        """
        me = f'{self.__class__.__name__}'
        if self._nickname:
            me += f'_{self._nickname}'
        try:
            return '.'.join([self.parent.name, me])
        except AttributeError:
            return me

    @property
    def fullname(self):
        """The SnoutAgent's fullname, guaranteed to be unique.

        Returns:
            str: The SnoutAgent's fullname, guaranteed to be unique.
        """
        return f'{self.name}@{hex(id(self))}'

    @property
    def statuslog(self):
        """Timestamped history of the SnoutAgent's status

        Returns:
            list: A list of (timestamp, old_status, new_status) tuples.
        """
        return self._statuslog

    @property
    def status(self):
        """The current status of the SnoutAgent.

        Returns:
            Status: The current status of the SnoutAgent.
        """
        return self._status

    @status.setter
    def status(self, value):
        # if isinstance(value, Status):
        if value != self._status:
            self.logger.debug(f'Status {repr(self._status)} -> {repr(value)}')
            self.statuslog.append((time.time(), self._status, value))
            self._status = value
        # else:
        #    raise TypeError(
        #        f"The status of {self.__class__.__name__} must be a Status flag.")

    def arg_override(self, *args, **kwargs):
        oargs = self.args + args
        okwargs = dict(self.kwargs, **kwargs)
        return (oargs, okwargs)

    def run(self, *args, **kwargs):
        self.status = Status.Running
        # create argument set from base arguments + custom arguments
        oargs, okwargs = self.arg_override(*args, **kwargs)
        self.runlogic(oargs, okwargs)
        self.status = Status.Complete

    def runlogic(self, *args, **kwargs):
        raise NotImplementedError(
            f'Please subclass SnoutAgent.runlogic() in {self.__class__.__name__}.'
        )

    def stop(self):
        if self.status & Status.Running:
            self.status |= Status.Stopping
        self.stoplogic()
        self.status = (self.status & ~(Status.Running | Status.Stopping)) | Status.Stopped

    def stoplogic(self):
        raise NotImplementedError(
            f'Please subclass SnoutAgent.stoplogic() in {self.__class__.__name__}.'
        )
