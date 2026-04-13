class ServiceError(Exception):
    """Base class for service-layer exceptions."""


class ValidationError(ServiceError):
    """Raised when input data is invalid."""


class NotFoundError(ServiceError):
    """Raised when a requested record does not exist."""


class ConflictError(ServiceError):
    """Raised when a unique/conflict rule is violated."""


class AuthenticationError(ServiceError):
    """Raised when authentication fails."""


class AuthorizationError(ServiceError):
    """Raised when authorization fails."""


from app.services.auth_service import AuthService
from app.services.employee_service import EmployeeService
from app.services.department_service import DepartmentService
from app.services.audit_service import AuditService

__all__ = [
    "ServiceError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "AuthenticationError",
    "AuthorizationError",
    "AuthService",
    "EmployeeService",
    "DepartmentService",
    "AuditService",
]