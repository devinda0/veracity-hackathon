class APIException(Exception):
    def __init__(self, detail: str, status_code: int = 400, error_code: str = "GENERIC") -> None:
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)


class AuthException(APIException):
    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(detail=detail, status_code=401, error_code="UNAUTHORIZED")


class NotFoundException(APIException):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail=detail, status_code=404, error_code="NOT_FOUND")

