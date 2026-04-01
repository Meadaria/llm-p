class BaseAppError(Exception):
    def __init__(self, message="An error occurred", details=None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConflictError(BaseAppError):
    def __init__(self, resource, value, details=None):
        message = f"{resource} '{value}' already exists"
        super().__init__(message, details)
        self.resource = resource
        self.value = value


class UnauthorizedError(BaseAppError):
    def __init__(self, reason="Invalid credentials", details=None):
        super().__init__(reason, details)
        self.reason = reason


class ForbiddenError(BaseAppError):
    def __init__(self, action="perform this action", details=None):
        message = f"You don't have permission to {action}"
        super().__init__(message, details)
        self.action = action


class NotFoundError(BaseAppError):
    def __init__(self, resource, identifier=None, details=None):
        message = f"{resource} not found"
        if identifier:
            message += f" (id: {identifier})"
        super().__init__(message, details)
        self.resource = resource
        self.identifier = identifier


class ExternalServiceError(BaseAppError):
    def __init__(self, service_name, status_code=None, response=None, details=None):
        message = f"External service '{service_name}' error"
        if status_code:
            message += f" (status: {status_code})"
        super().__init__(message, details)
        self.service_name = service_name
        self.status_code = status_code
        self.response = response