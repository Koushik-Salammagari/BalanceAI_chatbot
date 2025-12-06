import json
from typing import Dict
from pathlib import Path
from config.settings import DYNAMODB_MOCK_PATH
from utils.error_handler import handle_tool_error


@handle_tool_error("DynamoDB Query")
def query_dynamodb(apartment_number: str, unit_number: str) -> Dict:
    """
    Query DynamoDB for unit metadata.
    
    Args:
        apartment_number: Apartment/building number (e.g., "4")
        unit_number: Unit number (e.g., "12H")
    
    Returns:
        Dict with unit metadata or error message
    """
    # Validate inputs
    if not apartment_number or not unit_number:
        return {
            "success": False,
            "error": "Both apartment number and unit number are required",
            "error_type": "INVALID_INPUT"
        }
    
    # Check if file exists
    if not Path(DYNAMODB_MOCK_PATH).exists():
        raise FileNotFoundError(f"Mock data file not found: {DYNAMODB_MOCK_PATH}")
    
    # Load mock data
    with open(DYNAMODB_MOCK_PATH, 'r') as f:
        data = json.load(f)
    
    # Validate data structure
    if 'units' not in data:
        raise KeyError("'units' key not found in DynamoDB mock data")
    
    # Search for matching unit
    for unit in data['units']:
        if (unit.get('apartment_number') == str(apartment_number) and 
            unit.get('unit_number') == str(unit_number).upper()):
            return {
                "success": True,
                "data": unit
            }
    
    # No match found
    return {
        "success": False,
        "error": f"Unit {unit_number} in apartment {apartment_number} not found",
        "error_type": "UNIT_NOT_FOUND"
    }