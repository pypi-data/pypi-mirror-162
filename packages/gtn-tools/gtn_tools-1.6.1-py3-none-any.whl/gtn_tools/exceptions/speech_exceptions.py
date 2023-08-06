class GoogleAPIException(Exception):
    """
    This class is base of All Memsource exceptions.
    """
    message_prefix = "The Google API returned an error."


class FileException(Exception):
    message_prefix = "Error processing the input file."


class InvalidArgumentException(GoogleAPIException):
    def __init__(self, status_code, error):
        self.status_code = status_code
        self.error = error

        message = (f"{self.message_prefix} "
                   f"http status code: {status_code} "
                   f"error description: {error} ")

        super(InvalidArgumentException, self).__init__(message)


class InvalidAudioFormatException(FileException):
    def __init__(self, status_code, error):
        self.status_code = status_code
        self.error = error

        message = (f"{self.message_prefix} "
                   f"http status code: {status_code} "
                   f"error description: {error} ")

        super(InvalidArgumentException, self).__init__(message)
