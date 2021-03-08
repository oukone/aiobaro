class LoginRequiredException(Exception):
    def __init__(self, status_code=None, message=None):
        self.status_code = status_code
        self.message = message
        super().__init__(message)
