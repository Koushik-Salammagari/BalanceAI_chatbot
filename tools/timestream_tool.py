import json
from typing import Dict
from datetime import datetime
from pathlib import Path
from config.settings import TIMESTREAM_MOCK_PATH
from utils.error_handler import handle_tool_error


@handle_tool_error("Timestream Query")
def query_timestream(
    unit_id: str,
    start_time: str,
    end_time: str
) -> Dict:
    """
    Query Timestream for sensor data.
    
    Args:
        unit_id: Unit identifier (e.g., "apt4-12H-002")
        start_time: Start timestamp (ISO format: "2025-10-27T14:00:00Z")
        end_time: End timestamp (ISO format: "2025-10-27T17:00:00Z")
    
    Returns:
        Dict with sensor readings and statistics
    """
    # Validate inputs
    if not unit_id or not start_time or not end_time:
        return {
            "success": False,
            "error": "unit_id, start_time, and end_time are required",
            "error_type": "INVALID_INPUT"
        }
    
    # Check if file exists
    if not Path(TIMESTREAM_MOCK_PATH).exists():
        raise FileNotFoundError(f"Mock data file not found: {TIMESTREAM_MOCK_PATH}")
    
    # Parse and validate time range
    try:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        if start_dt >= end_dt:
            return {
                "success": False,
                "error": "start_time must be before end_time",
                "error_type": "INVALID_TIME"
            }
    except (ValueError, AttributeError) as e:
        return {
            "success": False,
            "error": f"Invalid time format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ): {str(e)}",
            "error_type": "INVALID_TIME"
        }
    
    # Load mock data
    with open(TIMESTREAM_MOCK_PATH, 'r') as f:
        data = json.load(f)
    
    # Validate data structure
    if 'readings' not in data:
        raise KeyError("'readings' key not found in Timestream mock data")
    
    # Filter readings
    filtered_readings = []
    for reading in data['readings']:
        if reading.get('unit_id') == unit_id:
            try:
                reading_time = datetime.fromisoformat(
                    reading['timestamp'].replace('Z', '+00:00')
                )
                if start_dt <= reading_time <= end_dt:
                    filtered_readings.append(reading)
            except (KeyError, ValueError):
                continue  # Skip malformed readings
    
    if not filtered_readings:
        return {
            "success": False,
            "error": f"No sensor data found for unit {unit_id} between {start_time} and {end_time}",
            "error_type": "NO_DATA"
        }
    
    # Calculate statistics
    try:
        temps = [r['temperature'] for r in filtered_readings]
        humidities = [r['humidity'] for r in filtered_readings]
        
        stats = {
            "count": len(filtered_readings),
            "temperature": {
                "avg": round(sum(temps) / len(temps), 2),
                "min": round(min(temps), 2),
                "max": round(max(temps), 2)
            },
            "humidity": {
                "avg": round(sum(humidities) / len(humidities), 2),
                "min": round(min(humidities), 2),
                "max": round(max(humidities), 2)
            }
        }
    except (KeyError, ZeroDivisionError) as e:
        return {
            "success": False,
            "error": f"Error calculating statistics: {str(e)}",
            "error_type": "INVALID_DATA"
        }
    
    return {
        "success": True,
        "data": {
            "readings": filtered_readings,
            "statistics": stats
        }
    }