import requests
from langchain.tools import tool
from config.settings import API_BASE_URL, API_GATEWAY_KEY
from utils.error_handler import handle_tool_error, ToolError
from datetime import datetime, timedelta
import logging
from typing import Optional

logger = logging.getLogger(__name__)


@handle_tool_error
@tool
def get_sensor_data(
    unit_id: str,
    start_time: str,
    end_time: str,
    data_type: str = 'all'
):
    """
    Get sensor data (temperature, humidity, presence) for a unit within a time range.
    
    Args:
        unit_id: Unit identifier (e.g., 'unit118')
        start_time: Start time in ISO format (e.g., '2025-12-01T00:00:00Z')
        end_time: End time in ISO format (e.g., '2025-12-06T23:59:59Z')
        data_type: Type of data - 'temperature', 'humidity', 'presence', or 'all' (default: 'all')
    
    Returns:
        Dictionary with sensor readings and statistics
    
    Example:
        get_sensor_data('unit118', '2025-12-06T00:00:00Z', '2025-12-06T23:59:59Z', 'temperature')
    """
    logger.info(f"Getting sensor data for {unit_id}, type={data_type}")
    
    url = f"{API_BASE_URL}/sensor-data"
    
    headers = {
        'x-api-key': API_GATEWAY_KEY
    }
    
    params = {
        'unit_id': unit_id,
        'start_time': start_time,
        'end_time': end_time,
        'data_type': data_type
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)  # ← FIXED: Added headers=headers
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('success'):
            raise ToolError(
                error_type='API_ERROR',
                message=f"API returned error: {data.get('error', 'Unknown error')}"
            )
        
        logger.info(f"Successfully retrieved sensor data for {unit_id}")
        return data['data']
        
    except requests.exceptions.Timeout:
        raise ToolError(
            error_type='TIMEOUT',
            message=f"Request timed out while getting sensor data for {unit_id}"
        )
    except requests.exceptions.RequestException as e:
        raise ToolError(
            error_type='API_ERROR',
            message=f"Failed to get sensor data: {str(e)}"
        )


@handle_tool_error
@tool
def get_recent_sensor_data(unit_id: str, days: int = 7, data_type: str = 'all'):
    """
    Get sensor data for the last N days (convenience function).
    
    Args:
        unit_id: Unit identifier
        days: Number of days to retrieve (default: 7)
        data_type: Type of data - 'temperature', 'humidity', 'presence', or 'all'
    
    Returns:
        Dictionary with sensor readings and statistics
    
    Example:
        get_recent_sensor_data('unit118', days=7, data_type='temperature')
    """
    logger.info(f"Getting last {days} days of data for {unit_id}")
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    
    return get_sensor_data.invoke({
        'unit_id': unit_id,
        'start_time': start_str,
        'end_time': end_str,
        'data_type': data_type
    })