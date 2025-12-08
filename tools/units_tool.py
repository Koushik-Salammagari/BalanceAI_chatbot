import requests
from typing import Optional
from langchain.tools import tool
from config.settings import API_BASE_URL, API_GATEWAY_KEY
from utils.error_handler import handle_tool_error, ToolError
import logging

logger = logging.getLogger(__name__)


@handle_tool_error
@tool
def get_unit_metadata(unit_id: str):
    """
    Get detailed metadata for a specific unit including sensors, location, and property info.
    
    Args:
        unit_id: Unit identifier (e.g., 'unit118', 'unit115')
    
    Returns:
        Dictionary with unit details and sensors
    
    Example:
        get_unit_metadata('unit118')
    """
    logger.info(f"Getting metadata for unit: {unit_id}")

    if API_GATEWAY_KEY:
        logger.info(f"API Key (first 10 chars): {API_GATEWAY_KEY[:10]}...")
    else:
        logger.info("API Key is None or empty!")
    
    url = f"{API_BASE_URL}/units/{unit_id}"
    
    headers = {
        'x-api-key': API_GATEWAY_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)  # ← FIXED: Added headers=headers
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('success'):
            raise ToolError(
                error_type='API_ERROR',
                message=f"API returned error: {data.get('error', 'Unknown error')}"
            )
        
        logger.info(f"Successfully retrieved metadata for {unit_id}")
        return data['data']
        
    except requests.exceptions.Timeout:
        raise ToolError(
            error_type='TIMEOUT',
            message=f"Request timed out while getting unit {unit_id}"
        )
    except requests.exceptions.RequestException as e:
        raise ToolError(
            error_type='API_ERROR',
            message=f"Failed to get unit metadata: {str(e)}"
        )


@handle_tool_error
@tool
def list_units(
    property_name: Optional[str] = None,
    floor: Optional[str] = None,
    unit_name: Optional[str] = None,
    limit: int = 50
):
    """
    List and search units with optional filters.
    
    Args:
        property_name: Filter by property name (optional)
        floor: Filter by floor number (optional)
        unit_name: Search by unit name (optional)
        limit: Maximum number of results (default: 50, max: 100)
    
    Returns:
        Dictionary with list of units and total count
    
    Examples:
        list_units() - Get all units
        list_units(property_name='Market Lofts') - Get units in Market Lofts
        list_units(floor='1') - Get units on floor 1
    """
    logger.info(f"Listing units with filters: property={property_name}, floor={floor}, name={unit_name}")
    
    url = f"{API_BASE_URL}/units"

    headers = {
        'x-api-key': API_GATEWAY_KEY
    }
    
    # Build query parameters
    params = {}
    if property_name:
        params['property_name'] = property_name
    if floor:
        params['floor'] = floor
    if unit_name:
        params['unit_name'] = unit_name
    if limit:
        params['limit'] = limit
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)  # ← This one is correct!
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('success'):
            raise ToolError(
                error_type='API_ERROR',
                message=f"API returned error: {data.get('error', 'Unknown error')}"
            )
        
        logger.info(f"Successfully retrieved {data['data']['total_count']} units")
        return data['data']
        
    except requests.exceptions.RequestException as e:
        raise ToolError(
            error_type='API_ERROR',
            message=f"Failed to list units: {str(e)}"
        )