import logging

logger = logging.getLogger(__name__)


class ToolError(Exception):
    """Custom exception for tool errors"""
    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(self.message)


def handle_tool_error(func):
    """
    Decorator to handle errors in tool functions.
    Preserves the original function's docstring and metadata.
    """
    # If func is already a tool (has 'invoke' method), just return it
    if hasattr(func, 'invoke'):
        return func
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ToolError as e:
            logger.error(f"Tool error in {func.__name__}: {e.error_type} - {e.message}")
            return {
                'error': True,
                'error_type': e.error_type,
                'message': e.message
            }
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            return {
                'error': True,
                'error_type': 'UNKNOWN_ERROR',
                'message': f"An unexpected error occurred: {str(e)}"
            }
    
    # Preserve original function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    if hasattr(func, '__annotations__'):
        wrapper.__annotations__ = func.__annotations__
    if hasattr(func, '__module__'):
        wrapper.__module__ = func.__module__
    
    return wrapper


def format_user_error(error_response: dict) -> str:
    """
    Format error response for user-friendly display.
    
    Args:
        error_response: Dictionary with error information
    
    Returns:
        Formatted error message string
    """
    if not isinstance(error_response, dict) or not error_response.get('error'):
        return "An unknown error occurred."
    
    error_type = error_response.get('error_type', 'UNKNOWN_ERROR')
    message = error_response.get('message', 'No details available')
    
    # Error type emoji mapping
    emoji_map = {
        'FILE_NOT_FOUND': '📁',
        'INVALID_DATA': '⚠️',
        'UNIT_NOT_FOUND': '🔍',
        'NO_DATA': '📊',
        'INVALID_TIME': '⏰',
        'API_ERROR': '🌐',
        'TIMEOUT': '⏱️',
        'UNKNOWN_ERROR': '❌'
    }
    
    emoji = emoji_map.get(error_type, '❌')
    
    return f"{emoji} {message}"