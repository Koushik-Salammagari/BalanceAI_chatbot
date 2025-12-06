from typing import Dict, Any
from functools import wraps
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ToolError(Exception):
    """Custom exception for tool errors"""
    def __init__(self, message: str, error_type: str = "GENERAL_ERROR"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


def handle_tool_error(tool_name: str):
    """
    Decorator for handling tool errors gracefully.
    
    Args:
        tool_name: Name of the tool for logging
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            try:
                logger.info(f"Executing {tool_name} with args: {kwargs}")
                result = func(*args, **kwargs)
                
                if result.get("success"):
                    logger.info(f"{tool_name} executed successfully")
                else:
                    logger.warning(f"{tool_name} returned error: {result.get('error')}")
                
                return result
                
            except FileNotFoundError as e:
                error_msg = f"Data file not found. Please check configuration."
                logger.error(f"{tool_name} - FileNotFoundError: {str(e)}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "FILE_NOT_FOUND"
                }
            
            except ValueError as e:
                error_msg = f"Invalid data format: {str(e)}"
                logger.error(f"{tool_name} - ValueError: {str(e)}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "INVALID_DATA"
                }
            
            except KeyError as e:
                error_msg = f"Missing required field in data: {str(e)}"
                logger.error(f"{tool_name} - KeyError: {str(e)}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "MISSING_FIELD"
                }
            
            except Exception as e:
                error_msg = f"Unexpected error occurred: {str(e)}"
                logger.error(f"{tool_name} - Unexpected error: {str(e)}", exc_info=True)
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "UNEXPECTED_ERROR"
                }
        
        return wrapper
    return decorator


def format_user_error(error_response: Dict[str, Any]) -> str:
    """
    Format error response into user-friendly message.
    
    Args:
        error_response: Error dictionary from tool
        
    Returns:
        Formatted error message
    """
    error_type = error_response.get("error_type", "GENERAL_ERROR")
    error_msg = error_response.get("error", "An error occurred")
    
    error_templates = {
        "FILE_NOT_FOUND": "⚠️ System configuration issue. Please contact support.",
        "INVALID_DATA": f"⚠️ Data format error: {error_msg}",
        "MISSING_FIELD": f"⚠️ Incomplete data: {error_msg}",
        "UNIT_NOT_FOUND": f"❌ {error_msg}\n\nPlease check the unit number and apartment number.",
        "NO_DATA": f"📭 {error_msg}\n\nTry a different time range or unit.",
        "INVALID_TIME": f"⏰ {error_msg}\n\nPlease use format: 'YYYY-MM-DDTHH:MM:SSZ'",
        "UNEXPECTED_ERROR": f"❌ Something went wrong: {error_msg}\n\nPlease try again."
    }
    
    return error_templates.get(error_type, f"❌ {error_msg}")