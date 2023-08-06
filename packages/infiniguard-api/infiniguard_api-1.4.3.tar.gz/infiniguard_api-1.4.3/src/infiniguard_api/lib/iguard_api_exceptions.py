class IguardApiException(Exception):
    pass


class IguardApiWithCodeException(Exception):
    def __init__(self, error, code):
        self.error = error
        self.code = code
        super(IguardApiWithCodeException, self).__init__()


class IguardApiFieldException(Exception):
    pass


class IguardApiQueryException(Exception):
    pass


class IguardApiFilterException(Exception):
    pass
