from typing_extensions import Final

from ._typing import ResponseErrors

__all__ = (
    "ERRORS",
    "INVALID_JSON",
    "INVALID_CONTENT",
    "LOGIN_FAILED",
    "BAD_VERSION",
    "UNKNOWN_OPERATION",
    "SERVER_ERROR",
    "UNSUPPORTED_OPERATION",
    "INVALID_ACTION",
)

INVALID_JSON: Final = 1
INVALID_CONTENT: Final = 2
LOGIN_FAILED: Final = 3
BAD_VERSION: Final = 4
UNKNOWN_OPERATION: Final = 5
SERVER_ERROR: Final = 6
UNSUPPORTED_OPERATION: Final = 7
INVALID_ACTION: Final = 8

ERRORS: ResponseErrors = {
    INVALID_JSON: (
        "INVALID_JSON",
        "Invalid JSON structure was received.",
    ),
    INVALID_CONTENT: (
        "INVALID_CONTENT",
        "JSON content is invalid.",
    ),
    LOGIN_FAILED: (
        "LOGIN_FAILED",
        "Login token is invalid.",
    ),
    BAD_VERSION: (
        "BAD_VERSION",
        "Version of client is not high enough.",
    ),
    UNKNOWN_OPERATION: (
        "UNKNOWN_OPERATION",
        "Operation not found.",
    ),
    SERVER_ERROR: (
        "SERVER_ERROR",
        "Internal server error.",
    ),
    UNSUPPORTED_OPERATION: (
        "UNSUPPORTED_OPERATION",
        "Request operation is not supported by the server.",
    ),
    INVALID_ACTION: (
        "INVALID_ACTION",
        "Invalid action was sent.",
    ),
}
