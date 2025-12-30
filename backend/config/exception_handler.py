"""
Custom exception handler for sanitized API error responses.
Prevents leaking sensitive information in error messages.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

logger = logging.getLogger('django.security')

# Generic error messages for security-sensitive errors
GENERIC_ERROR_MESSAGES = {
    400: 'Invalid request data.',
    401: 'Authentication credentials were not provided or are invalid.',
    403: 'You do not have permission to perform this action.',
    404: 'The requested resource was not found.',
    405: 'Method not allowed.',
    429: 'Too many requests. Please try again later.',
    500: 'An internal server error occurred.',
}


def custom_exception_handler(exc, context):
    """
    Custom exception handler that sanitizes error responses.

    - Prevents leaking database structure in errors
    - Logs detailed errors server-side for debugging
    - Returns generic messages to clients for sensitive errors
    """
    # Get the standard error response
    response = exception_handler(exc, context)

    # Get request info for logging
    request = context.get('request')
    view = context.get('view')

    # Log the full exception for debugging
    logger.warning(
        f"API Exception: {exc.__class__.__name__} - {str(exc)} | "
        f"View: {view.__class__.__name__ if view else 'Unknown'} | "
        f"User: {getattr(request, 'user', 'Anonymous')} | "
        f"Path: {getattr(request, 'path', 'Unknown')}"
    )

    if response is not None:
        # Sanitize certain error types
        status_code = response.status_code

        # For server errors, always return generic message
        if status_code >= 500:
            response.data = {
                'error': GENERIC_ERROR_MESSAGES.get(500),
                'status_code': status_code
            }

        # For 401/403, don't leak whether user exists
        elif status_code in [401, 403]:
            # Keep error message but ensure it's generic
            if isinstance(response.data, dict):
                response.data = {
                    'error': response.data.get('detail', GENERIC_ERROR_MESSAGES.get(status_code)),
                    'status_code': status_code
                }
            else:
                response.data = {
                    'error': GENERIC_ERROR_MESSAGES.get(status_code),
                    'status_code': status_code
                }

        # For validation errors (400), sanitize database-related messages
        elif status_code == 400:
            if isinstance(response.data, dict):
                sanitized_data = {}
                for key, value in response.data.items():
                    # Sanitize values that might leak database info
                    if isinstance(value, list):
                        sanitized_data[key] = [
                            sanitize_error_message(str(v)) for v in value
                        ]
                    elif isinstance(value, str):
                        sanitized_data[key] = sanitize_error_message(value)
                    else:
                        sanitized_data[key] = value
                response.data = sanitized_data

        # Add status code to response for consistency
        if isinstance(response.data, dict) and 'status_code' not in response.data:
            response.data['status_code'] = status_code

    return response


def sanitize_error_message(message: str) -> str:
    """
    Sanitize error messages to remove potentially sensitive information.
    """
    # Keywords that might indicate database/internal structure leakage
    sensitive_patterns = [
        'DETAIL:',
        'SQL',
        'column',
        'table',
        'constraint',
        'foreign key',
        'IntegrityError',
        'OperationalError',
        'ProgrammingError',
        'psycopg2',
        'postgresql',
        'mysql',
        'sqlite',
        '/app/',
        '/home/',
        'Traceback',
        'File "',
        'line ',
    ]

    message_lower = message.lower()
    for pattern in sensitive_patterns:
        if pattern.lower() in message_lower:
            return 'An error occurred while processing your request.'

    return message
