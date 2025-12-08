import requests
from langchain.tools import tool
from config.settings import API_BASE_URL, API_GATEWAY_KEY
from utils.error_handler import handle_tool_error, ToolError
from datetime import datetime, timedelta
import logging
from typing import List

logger = logging.getLogger(__name__)


@handle_tool_error
@tool
def get_temperature_trends(unit_id: str, days: int = 7, metric: str = 'temperature'):
    """
    Analyze temperature or humidity trends over time.
    
    Args:
        unit_id: Unit identifier (e.g., 'unit118')
        days: Number of days to analyze (1-30, default: 7)
        metric: 'temperature', 'humidity', or 'both' (default: 'temperature')
    
    Returns:
        Dictionary with trend analysis (direction, change, daily averages)
    
    Example:
        get_temperature_trends('unit118', days=7, metric='temperature')
    """
    logger.info(f"Analyzing trends for {unit_id}, metric={metric}, days={days}")
    
    url = f"{API_BASE_URL}/analytics/trends"
    
    headers = {
        'x-api-key': API_GATEWAY_KEY
    }
    
    params = {
        'unit_id': unit_id,
        'days': days,
        'metric': metric
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
        
        logger.info(f"Successfully analyzed trends for {unit_id}")
        return data['data']
        
    except requests.exceptions.RequestException as e:
        raise ToolError(
            error_type='API_ERROR',
            message=f"Failed to get trends: {str(e)}"
        )


@handle_tool_error
@tool
def compare_units(unit_ids: List[str], start_time: str, end_time: str, metric: str = 'both'):
    """
    Compare sensor data across multiple units.
    
    Args:
        unit_ids: List of unit IDs to compare (2-5 units)
        start_time: Start time in ISO format
        end_time: End time in ISO format
        metric: 'temperature', 'humidity', or 'both' (default: 'both')
    
    Returns:
        Dictionary with comparison data and summary
    
    Example:
        compare_units(['unit118', 'unit111'], '2025-12-05T00:00:00Z', '2025-12-06T23:59:59Z')
    """
    logger.info(f"Comparing units: {unit_ids}")
    
    url = f"{API_BASE_URL}/analytics/compare"
    
    headers = {
        'x-api-key': API_GATEWAY_KEY
    }
    
    # Convert list to comma-separated string
    unit_ids_str = ','.join(unit_ids)
    
    params = {
        'unit_ids': unit_ids_str,
        'start_time': start_time,
        'end_time': end_time,
        'metric': metric
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
        
        logger.info(f"Successfully compared {len(unit_ids)} units")
        return data['data']
        
    except requests.exceptions.RequestException as e:
        raise ToolError(
            error_type='API_ERROR',
            message=f"Failed to compare units: {str(e)}"
        )


@handle_tool_error
@tool
def compare_recent_units(unit_ids: List[str], days: int = 7, metric: str = 'both'):
    """
    Compare units using recent data (convenience function).
    
    Args:
        unit_ids: List of unit IDs to compare
        days: Number of days to compare (default: 7)
        metric: 'temperature', 'humidity', or 'both'
    
    Returns:
        Dictionary with comparison data
    
    Example:
        compare_recent_units(['unit118', 'unit111'], days=7)
    """
    logger.info(f"Comparing {len(unit_ids)} units for last {days} days")
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    
    return compare_units.invoke({
        'unit_ids': unit_ids,
        'start_time': start_str,
        'end_time': end_str,
        'metric': metric
    })


@handle_tool_error
@tool
def get_system_statistics():
    """
    Get system-wide statistics (total units, properties, sensors).
    
    This is a derived function that uses list_units to calculate stats.
    
    Returns:
        Dictionary with system statistics
    
    Example:
        get_system_statistics()
    """
    logger.info("Getting system statistics")
    
    from tools.units_tool import list_units
    
    # Get all units
    units_data = list_units.invoke({'limit': 100})
    
    units = units_data.get('units', [])
    
    # Calculate statistics
    total_units = len(units)
    properties = {}
    total_sensors = 0
    
    for unit in units:
        prop = unit.get('property_name', 'Unknown')
        if prop not in properties:
            properties[prop] = 0
        properties[prop] += 1
        total_sensors += unit.get('sensor_count', 0)
    
    return {
        'total_units': total_units,
        'total_properties': len(properties),
        'total_sensors': total_sensors,
        'properties': [
            {'property_name': name, 'unit_count': count}
            for name, count in properties.items()
        ]
    }