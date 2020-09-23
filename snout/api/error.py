# SnoutAgent errors
class AmbiguousAgentError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AmbiguousSnoutfileError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AgentNotFoundError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# Experiment errors
class ExperimentException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ExperimentNotReadyException(ExperimentException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
