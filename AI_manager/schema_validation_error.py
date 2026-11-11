class SchemaValidationError(Exception):
    # Raised when the AI consistently returns invalid JSON schemas.
    def __init__(self, message="The AI returned an invalid or malformed JSON schema."):
        super().__init__(message)