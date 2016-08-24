

class InvalidRequestMethod(Exception):
    """Raise an invalid request method """
    def __init__(self, message, payload):
        super(InvalidRequestMethod, self).__init__(message, payload)

        self.message = message
        self.payload = payload

class TintriError(Exception):
    """Raise an invalid filter message"""
    def __init__(self, message, code):
        super(TintriError, self).__init__(message, code)

        self.message = message
        self.code = code