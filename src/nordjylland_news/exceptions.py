class InternalServerErrorException(Exception):
    pass


class ServiceUnavailableException(Exception):
    pass


class StatusCodeException(Exception):
    pass


class TooManyRequestsException(Exception):
    pass
