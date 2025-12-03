class RefreshError(Exception):
    """Exception raised when there is an error refreshing OAuth credentials."""

    def __init__(self, message: str, error: Exception | None = None, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.error = error

    def __repr__(self):
        return (
            super().__repr__()
            + f" (error: {self.error.__repr__() if self.error else ''})"
        )
