import json
from typing import Dict, List
from datetime import datetime
from config.settings import TIMESTREAM_MOCK_PATH


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
    try:
        # Load mock data
        with open(TIMESTREAM_MOCK_PATH, 'r') as f:
            data = json.load(f)
        
        # Parse time range
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # Filter readings
        filtered_readings = []
        for reading in data['readings']:
            if reading['unit_id'] == unit_id:
                reading_time = datetime.fromisoformat(
                    reading['timestamp'].replace('Z', '+00:00')
                )
                if start_dt <= reading_time <= end_dt:
                    filtered_readings.append(reading)
        
        if not filtered_readings:
            return {
                "success": False,
                "error": f"No data found for unit {unit_id} in specified time range"
            }
        
        # Calculate statistics
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
        
        return {
            "success": True,
            "data": {
                "readings": filtered_readings,
                "statistics": stats
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error querying Timestream: {str(e)}"
        }