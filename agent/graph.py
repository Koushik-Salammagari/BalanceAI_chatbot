from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from config.settings import (
    LLM_PROVIDER,
    LLM_MODEL,
    LLM_TEMPERATURE,
    ANTHROPIC_API_KEY,
    OPENAI_API_KEY
)
from tools import (
    query_dynamodb,
    query_timestream,
    get_units_in_apartment,
    query_date_range,
    compare_units,
    analyze_trend,
    get_system_stats
    
)


# Wrap basic tools with LangChain @tool decorator
@tool
def get_unit_metadata(apartment_number: str, unit_number: str) -> dict:
    """
    Get metadata for a specific unit.
    
    Args:
        apartment_number: Apartment/building number (e.g., "4")
        unit_number: Unit number (e.g., "12H")
    
    Returns:
        Unit metadata including unit_id, resident name, building, floor
    """
    return query_dynamodb(apartment_number, unit_number)


@tool
def get_sensor_data(unit_id: str, start_time: str, end_time: str) -> dict:
    """
    Get temperature and humidity sensor data for a unit within a time range.
    
    Args:
        unit_id: Unit identifier (e.g., "apt4-12H-007")
        start_time: Start timestamp in ISO format (e.g., "2025-10-27T14:00:00Z")
        end_time: End timestamp in ISO format (e.g., "2025-10-27T17:00:00Z")
    
    Returns:
        Sensor readings with temperature/humidity statistics
    """
    return query_timestream(unit_id, start_time, end_time)


# Wrap advanced tools with LangChain @tool decorator
@tool
def list_units_in_apartment(apartment_number: str) -> dict:
    """
    Get all units in a specific apartment or building.
    
    Args:
        apartment_number: Apartment/building number (e.g., "4")
    
    Returns:
        List of all units in that apartment with their metadata
    """
    return get_units_in_apartment(apartment_number)


@tool
def get_recent_data(unit_id: str, days: int = 7) -> dict:
    """
    Get sensor data for the last N days for a specific unit.
    Use this for queries like "last 7 days", "past week", "recent data".
    
    Args:
        unit_id: Unit identifier (e.g., "apt4-12H-007")
        days: Number of days to look back (default: 7, max: 30)
    
    Returns:
        Sensor readings with statistics and daily averages
    """
    return query_date_range(unit_id, days)


@tool
def compare_multiple_units(unit_ids: list, days: int = 7) -> dict:
    """
    Compare sensor data across multiple units.
    Use this for queries like "compare unit X and Y", "which unit is warmer".
    
    Args:
        unit_ids: List of unit identifiers to compare (e.g., ["apt4-12H-007", "apt1-5A-001"])
        days: Number of days to analyze (default: 7)
    
    Returns:
        Side-by-side comparison of temperature and humidity statistics
    """
    return compare_units(unit_ids, days)


@tool
def get_temperature_trends(unit_id: str, days: int = 7) -> dict:
    """
    Analyze temperature and humidity trends over time.
    Use this for queries like "temperature trend", "is it getting warmer", "humidity changes".
    
    Args:
        unit_id: Unit identifier (e.g., "apt4-12H-007")
        days: Number of days to analyze (default: 7)
    
    Returns:
        Trend analysis showing if temperature/humidity is increasing or decreasing
    """
    return analyze_trend(unit_id, days)

@tool
def get_system_statistics() -> dict:
    """
    Get overall system statistics including total apartments, units, buildings.
    Use this for queries like "how many apartments", "total units", "system overview".
    
    Returns:
        System-wide statistics and counts
    """
    return get_system_stats()

def create_agent():
    """
    Create and configure the LangGraph agent with tools.
    
    Returns:
        Configured agent graph
    """
    # Initialize LLM based on provider
    if LLM_PROVIDER == "anthropic":
        llm = ChatAnthropic(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            api_key=ANTHROPIC_API_KEY
        )
    elif LLM_PROVIDER == "openai":
        llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            api_key=OPENAI_API_KEY
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")
    
    # Define all tools (basic + advanced)
    tools = [
        get_unit_metadata,
        get_sensor_data,
        list_units_in_apartment,
        get_recent_data,
        compare_multiple_units,
        get_temperature_trends,
        get_system_statistics
    ]
    
    # Create ReAct agent with all tools
    agent = create_react_agent(llm, tools)
    
    return agent