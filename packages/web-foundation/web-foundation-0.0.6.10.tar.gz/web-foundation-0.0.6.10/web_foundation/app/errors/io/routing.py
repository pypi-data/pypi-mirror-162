from web_foundation.app.errors.base_error import BaseAppError


class BaseRouterError(BaseAppError):
    base_ex: Exception

    def __init__(self, base_ex: Exception):
        self.base_ex = base_ex


class YamlRouterLoadFileError(BaseRouterError):
    def __str__(self):
        return f"Can't load file with routes, cause: {self.base_ex.__str__()}"
