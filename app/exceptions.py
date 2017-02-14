class APIException(Exception):
    status_code = 400

    def __init__(self, message):
        self.message = message


class ValidationError(APIException):
    status_code = 400
