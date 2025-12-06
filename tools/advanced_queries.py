import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from config.settings import DYNAMODB_MOCK_PATH, TIMESTREAM_MOCK_PATH
from utils.error_handler import handle_tool_error
from datetime import timezone

@handle_tool_error("Get All Units in Apartment")
def get_units_in_apartment(apartment_number: str) -> Dict:
    """
    Get all units in a specific apartment/building.
    
    Args:
        apartment_number: Apartment/building number (e.g., "4")
    
    Returns:
        Dict with list of all units in that apartment
    """
    if not apartment_number:
        return {
            "success": False,
            "error": "Apartment number is required",
            "error_type": "INVALID_INPUT"
        }
    
    if not Path(DYNAMODB_MOCK_PATH).exists():
        raise FileNotFoundError(f"Mock data file not found: {DYNAMODB_MOCK_PATH}")
    
    with open(DYNAMODB_MOCK_PATH, 'r') as f:
        data = json.load(f)
    
    matching_units = [
        unit for unit in data['units'] 
        if unit.get('apartment_number') == str(apartment_number)
    ]
    
    if not matching_units:
        return {
            "success": False,
            "error": f"No units found in apartment {apartment_number}",
            "error_type": "NO_DATA"
        }
    
    return {
        "success": True,
        "data": {
            "apartment_number": apartment_number,
            "unit_count": len(matching_units),
            "units": matching_units
        }
    }


@handle_tool_error("Date Range Query")
def query_date_range(unit_id: str, days: int = 7) -> Dict:
    """
    Get sensor data for the last N days.
    
    Args:
        unit_id: Unit identifier (e.g., "apt4-12H-007")
        days: Number of days to look back (default: 7)
    
    Returns:
        Dict with sensor readings for the date range
    """
    if not unit_id:
        return {
            "success": False,
            "error": "unit_id is required",
            "error_type": "INVALID_INPUT"
        }
    
    if days < 1 or days > 30:
        return {
            "success": False,
            "error": "Days must be between 1 and 30",
            "error_type": "INVALID_INPUT"
        }
    
    if not Path(TIMESTREAM_MOCK_PATH).exists():
        raise FileNotFoundError(f"Mock data file not found: {TIMESTREAM_MOCK_PATH}")
    
    # Calculate date range
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days)
    
    with open(TIMESTREAM_MOCK_PATH, 'r') as f:
        data = json.load(f)
    
    # Filter readings
    filtered_readings = []
    for reading in data['readings']:
        if reading.get('unit_id') == unit_id:
            try:
                reading_time = datetime.fromisoformat(
                    reading['timestamp'].replace('Z', '+00:00')
                )
                if start_time <= reading_time <= end_time:
                    filtered_readings.append(reading)
            except (KeyError, ValueError):
                continue
    
    if not filtered_readings:
        return {
            "success": False,
            "error": f"No sensor data found for unit {unit_id} in the last {days} days",
            "error_type": "NO_DATA"
        }
    
    # Calculate statistics
    temps = [r['temperature'] for r in filtered_readings]
    humidities = [r['humidity'] for r in filtered_readings]
    
    # Daily averages
    daily_data = {}
    for reading in filtered_readings:
        date = reading['timestamp'][:10]  # Extract date (YYYY-MM-DD)
        if date not in daily_data:
            daily_data[date] = {'temps': [], 'humidities': []}
        daily_data[date]['temps'].append(reading['temperature'])
        daily_data[date]['humidities'].append(reading['humidity'])
    
    daily_averages = []
    for date, values in sorted(daily_data.items()):
        daily_averages.append({
            'date': date,
            'avg_temperature': round(sum(values['temps']) / len(values['temps']), 2),
            'avg_humidity': round(sum(values['humidities']) / len(values['humidities']), 2)
        })
    
    stats = {
        "count": len(filtered_readings),
        "days": days,
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
            "unit_id": unit_id,
            "readings_count": len(filtered_readings),
            "statistics": stats,
            "daily_averages": daily_averages,
            "all_readings": filtered_readings
        }
    }


@handle_tool_error("Compare Units")
def compare_units(unit_ids: List[str], days: int = 7) -> Dict:
    """
    Compare sensor data across multiple units.
    
    Args:
        unit_ids: List of unit identifiers to compare
        days: Number of days to analyze (default: 7)
    
    Returns:
        Dict with comparison data
    """
    if not unit_ids or len(unit_ids) < 2:
        return {
            "success": False,
            "error": "At least 2 unit_ids are required for comparison",
            "error_type": "INVALID_INPUT"
        }
    
    if not Path(TIMESTREAM_MOCK_PATH).exists():
        raise FileNotFoundError(f"Mock data file not found: {TIMESTREAM_MOCK_PATH}")
    
    # Calculate date range
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days)
    
    with open(TIMESTREAM_MOCK_PATH, 'r') as f:
        data = json.load(f)
    
    # Collect data for each unit
    comparison = {}
    
    for unit_id in unit_ids:
        filtered_readings = []
        for reading in data['readings']:
            if reading.get('unit_id') == unit_id:
                try:
                    reading_time = datetime.fromisoformat(
                        reading['timestamp'].replace('Z', '+00:00')
                    )
                    if start_time <= reading_time <= end_time:
                        filtered_readings.append(reading)
                except (KeyError, ValueError):
                    continue
        
        if filtered_readings:
            temps = [r['temperature'] for r in filtered_readings]
            humidities = [r['humidity'] for r in filtered_readings]
            
            comparison[unit_id] = {
                "readings_count": len(filtered_readings),
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
        else:
            comparison[unit_id] = {
                "error": "No data available"
            }
    
    if not any('temperature' in v for v in comparison.values()):
        return {
            "success": False,
            "error": "No data found for any of the specified units",
            "error_type": "NO_DATA"
        }
    
    return {
        "success": True,
        "data": {
            "comparison": comparison,
            "days_analyzed": days,
            "units_compared": len(unit_ids)
        }
    }


@handle_tool_error("Trend Analysis")
def analyze_trend(unit_id: str, days: int = 7) -> Dict:
    """
    Analyze temperature and humidity trends over time.
    
    Args:
        unit_id: Unit identifier
        days: Number of days to analyze
    
    Returns:
        Dict with trend analysis
    """
    if not unit_id:
        return {
            "success": False,
            "error": "unit_id is required",
            "error_type": "INVALID_INPUT"
        }
    
    if not Path(TIMESTREAM_MOCK_PATH).exists():
        raise FileNotFoundError(f"Mock data file not found: {TIMESTREAM_MOCK_PATH}")
    
    # Calculate date range
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days)
    
    with open(TIMESTREAM_MOCK_PATH, 'r') as f:
        data = json.load(f)
    
    # Filter and sort readings
    filtered_readings = []
    for reading in data['readings']:
        if reading.get('unit_id') == unit_id:
            try:
                reading_time = datetime.fromisoformat(
                    reading['timestamp'].replace('Z', '+00:00')
                )
                if start_time <= reading_time <= end_time:
                    filtered_readings.append(reading)
            except (KeyError, ValueError):
                continue
    
    if not filtered_readings:
        return {
            "success": False,
            "error": f"No sensor data found for unit {unit_id} in the last {days} days",
            "error_type": "NO_DATA"
        }
    
    # Sort by timestamp
    filtered_readings.sort(key=lambda x: x['timestamp'])
    
    # Calculate trend (simple linear)
    temps = [r['temperature'] for r in filtered_readings]
    humidities = [r['humidity'] for r in filtered_readings]
    
    # Temperature trend
    temp_first_half = temps[:len(temps)//2]
    temp_second_half = temps[len(temps)//2:]
    temp_trend = "increasing" if sum(temp_second_half) > sum(temp_first_half) else "decreasing"
    temp_change = round(temps[-1] - temps[0], 2)
    
    # Humidity trend
    hum_first_half = humidities[:len(humidities)//2]
    hum_second_half = humidities[len(humidities)//2:]
    hum_trend = "increasing" if sum(hum_second_half) > sum(hum_first_half) else "decreasing"
    hum_change = round(humidities[-1] - humidities[0], 2)
    
    return {
        "success": True,
        "data": {
            "unit_id": unit_id,
            "period_days": days,
            "readings_analyzed": len(filtered_readings),
            "temperature_trend": {
                "direction": temp_trend,
                "change": temp_change,
                "start_value": temps[0],
                "end_value": temps[-1]
            },
            "humidity_trend": {
                "direction": hum_trend,
                "change": hum_change,
                "start_value": humidities[0],
                "end_value": humidities[-1]
            }
        }
    }