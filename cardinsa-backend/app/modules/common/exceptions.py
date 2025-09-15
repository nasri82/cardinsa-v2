from fastapi import HTTPException, status

class DomainError(Exception):
    pass

class NotFoundError(DomainError):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail)
        self.detail = detail

def http_not_found(detail: str = "Not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

def http_conflict(detail: str = "Conflict") -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

def http_bad_request(detail: str = "Bad request") -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
