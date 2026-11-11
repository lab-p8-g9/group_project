class AIConnectionError(Exception):
    # Raised when the AI API cannot be reached after retries.
    def __init__(self, message="Failed to connect to the AI service after maximum retries."):
        super().__init__(message)