from fastapi import HTTPException

class AppBaseException(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"

class LLMError(AppBaseException):
    status_code = 502
    code = "LLM_ERROR"

class ValidationError(AppBaseException):
    status_code = 400
    code = "VALIDATION_ERROR"

class DatabaseError(AppBaseException):
    status_code = 500
    code = "DB_ERROR"