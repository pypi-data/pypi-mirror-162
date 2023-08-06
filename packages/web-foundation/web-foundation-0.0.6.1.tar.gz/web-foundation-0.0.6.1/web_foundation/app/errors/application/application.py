class ApplicationError(Exception):
    def __init__(self, ex=None, message=None):
        if ex:
            self.message = str(ex)
        else:
            self.message = message
        super().__init__(self.message)


class InconsistencyError(ApplicationError):
    def __init__(self, ex=None, message=None):
        super().__init__(ex=ex, message=message)
