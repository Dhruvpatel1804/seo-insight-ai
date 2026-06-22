class InvalidURLError(Exception):
    """Raised when a URL fails validation or SSRF safety checks."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ScrapingError(Exception):
    """Raised when webpage scraping fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PageSpeedError(Exception):
    """Raised when PageSpeed Insights API calls fail."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class OpenAIAnalysisError(Exception):
    """Raised when OpenAI analysis fails or returns invalid data."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
