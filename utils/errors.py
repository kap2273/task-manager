class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(AppError):
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", status_code=404)

class ValidationError(AppError):
    def __init__(self, field: str, reason: str):
        super().__init__(f"Invalid {field}: {reason}", status_code=422)
