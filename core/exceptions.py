class AppError(Exception):
    """Base class for all application-specific exceptions."""
    def __init__(self, message="An unexpected error occurred.", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ServiceError(AppError):
    """Raised when a business logic failure occurs in the service layer."""
    pass

class FeatureDisabledError(AppError):
    """Raised when attempting to access a disabled feature."""
    def __init__(self, feature_name):
        self.feature_name = feature_name
        super().__init__(f"The feature '{feature_name}' is currently disabled.")
