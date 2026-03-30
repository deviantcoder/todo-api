from fastapi import status


class AppException(Exception):
    status_code: int
    detail: str

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.__class__.detail


class NotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'Not found'


class AlreadyExistsException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Already exists'


class InvalidCredentialsException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Invalid credentials'
