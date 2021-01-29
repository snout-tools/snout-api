from time import monotonic as timer

from snout.api.agent import SnoutAgent, Status
from snout.api.event import EventMgmtCapability
from snout.api.factory import Factory


class ExperimentAPI(SnoutAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def ready(self):
        return (self.status & Status.Idle) and (not self.status & Status.Failed)

    def wait_ready(self):
        raise NotImplementedError('ExperimentAPI does not directly implement wait_ready.')

    @property
    def runs(self):
        return self._runs

    @runs.setter
    def runs(self, value):
        self._runs = int(value)

    @property
    def runstatus(self):
        if Status.Running in self.status:
            return f'Experiment running {self.runs} runs of {self.parameter_variations} parameter variations ({len(self.steps)} experiment steps).'
        else:
            s = [
                (1 << i & self.status).name
                for i in range(self.status.bit_length())
                if 1 << i & self.status
            ]
            return 'Experiment {}.'.format(', '.join(s).lower())

    def coordinate(self, params, runid):
        raise NotImplementedError('ExperimentAPI does not directly implement a coordinate method.')

    def run(self):
        raise NotImplementedError('ExperimentAPI does not directly implement a run routine.')

    def runall(self):
        for _ in self.run():
            self.wait_ready()


class ExperimentClock:
    def __init__(self):
        self.reset()

    def __repr__(self):
        return f'ExperimentClock({repr(self.status)}, t={self.elapsed})'

    def start(self):
        self.status = Status.Running
        self.t_start = timer()

    def stop(self):
        self.t_active.append((self.t_start, timer()))
        self.status = Status.Stopped
        self.t_start = 0

    def reset(self):
        self.t_active = []
        self.t_start = 0
        self.status = Status.Idle

    @property
    def elapsed(self):
        return timer() - self.t_start if self.t_start > 0 else 0


class InstrumentAPI(SnoutAgent, EventMgmtCapability):

    __base_agent__ = 'instrument'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = kwargs.get('path', None)
        if (
            self.parent
            and not isinstance(self.parent, SnoutAgent)
            and self.parent.__class__.__name__ != 'Experiment'
        ):
            raise TypeError(
                f'The parent of {self.__class__.__name__} must be Experiment ({type(self.parent)} provided).'
            )

    def __repr__(self):
        return f'{self.name}({repr(self.args)}, {repr(self.kwargs)})'

    @property
    def protocol(self):
        raise NotImplementedError('Please subclass Instrument and implement the protocol property.')

    @property
    def info(self):
        raise NotImplementedError('Please subclass Instrument and implement the info property.')


class StepConditionAPI(SnoutAgent):

    __base_agent__ = 'stepcondition'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProcessingQueueAPI(SnoutAgent, EventMgmtCapability):

    __base_agent__ = 'processingqueue'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)