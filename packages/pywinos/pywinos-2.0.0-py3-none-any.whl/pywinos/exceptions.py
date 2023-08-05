__author__ = 'Andrey Komissarov'
__date__ = '2022'


class RemoteCommandExecutionError(BaseException):
    def __init__(self, error: str = None):
        self.error = error

    def __str__(self):
        return f'During handling remote command execution error occurred!\n{self.error}'


class LocalCommandExecutionError(BaseException):
    def __init__(self, error: str = None):
        self.error = error

    def __str__(self):
        return f'During handling local command execution error occurred!\n{self.error}'


class ServiceLookupError(BaseException):
    def __init__(self, name: str = None):
        self.name = name or 'name is not specified by user'

    def __str__(self):
        return f'Service ({self.name}) not found!'
