from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Custom exception handler that provides consistent error responses."""
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            'success': False,
            'status_code': response.status_code,
            'errors': response.data,
        }

        # Add message for common error codes
        status_messages = {
            400: 'Bad request.',
            401: 'Authentication credentials were not provided or are invalid.',
            403: 'You do not have permission to perform this action.',
            404: 'The requested resource was not found.',
            405: 'Method not allowed.',
            429: 'Request was throttled. Please try again later.',
        }
        custom_response['message'] = status_messages.get(
            response.status_code, 'An error occurred.'
        )

        response.data = custom_response

    else:
        # Handle unhandled exceptions
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        response = Response(
            {
                'success': False,
                'status_code': 500,
                'message': 'An internal server error occurred.',
                'errors': str(exc) if context.get('request') and hasattr(context['request'], 'user') and context['request'].user.is_staff else 'Internal server error.',
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def success_response(data=None, message="Success", status_code=200):
    """Helper for consistent success responses."""
    response = {
        'success': True,
        'status_code': status_code,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return Response(response, status=status_code)


def error_response(message="Error", errors=None, status_code=400):
    """Helper for consistent error responses."""
    response = {
        'success': False,
        'status_code': status_code,
        'message': message,
    }
    if errors is not None:
        response['errors'] = errors
    return Response(response, status=status_code)
