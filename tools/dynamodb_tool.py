import json
from typing import Dict, Optional
from config.settings import DYNAMODB_MOCK_PATH


def query_dynamodb(apartment_number: str, unit_number: str) -> Dict:
    """
    Query DynamoDB for unit metadata.
    
    Args:
        apartment_number: Apartment/building number (e.g., "4")
        unit_number: Unit number (e.g., "12H")
    
    Returns:
        Dict with unit metadata or error message
    """
    try:
        # Load mock data
        with open(DYNAMODB_MOCK_PATH, 'r') as f:
            data = json.load(f)
        
        # Search for matching unit
        for unit in data['units']:
            if (unit['apartment_number'] == apartment_number and 
                unit['unit_number'] == unit_number):
                return {
                    "success": True,
                    "data": unit
                }
        
        # No match found
        return {
            "success": False,
            "error": f"Unit {unit_number} in apartment {apartment_number} not found"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error querying DynamoDB: {str(e)}"
        }