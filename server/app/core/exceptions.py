import logging
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base class for predictable, domain-level errors (services raise these, never HTTPException)."""
    code = 'app_error'


    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, headers: dict[str, str] | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.headers = headers



class BadRequestException(AppException):
    code = 'bad_request'



class UnauthorizedException(AppException):
    code = 'unauthorized'
    
    def __init__(self, message: str = 'Not Authenticated'):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, {"WWW-Authenticate": "Bearer"})


class ForbiddenException(AppException):
    code = 'forbidden'
    def __init__(self, message: str = 'Insufficient permissions'):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundException(AppException):
    code = "not_found"

    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status.HTTP_404_NOT_FOUND)


class ConflictException(AppException):
    code = "conflict"

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class ServiceUnavailableException(AppException):
    code = "service_unavailable"

    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    'code': exc.code,
                    'message': exc.message
                }
            },
            headers=exc.headers
        )


    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception('Unhandled error on %s %s', request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'error': {
                    'code': 'internal_error',
                    'message': 'Internal Server Error'
                }
            },
        )