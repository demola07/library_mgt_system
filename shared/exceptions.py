from typing import Optional, Any, Dict

class LibraryException(Exception):
    """Base exception for library system"""
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class DatabaseOperationError(LibraryException):
    """Database operation failures"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details
        )

class ResourceNotFoundError(LibraryException):
    """Resource not found in database"""
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier {identifier} not found",
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)}
        )

class ValidationError(LibraryException):
    """Data validation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )

class MessageBrokerError(LibraryException):
    """Message broker operation failures"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="MESSAGE_BROKER_ERROR",
            status_code=500,
            details=details
        ) 