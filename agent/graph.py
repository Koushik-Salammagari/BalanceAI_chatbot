from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config.settings import (
    LLM_PROVIDER,
    LLM_MODEL,
    LLM_TEMPERATURE,
    ANTHROPIC_API_KEY,
    OPENAI_API_KEY
)

# Import NEW API-based tools
from tools.units_tool import get_unit_metadata, list_units
from tools.sensor_tool import get_sensor_data, get_recent_sensor_data
from tools.analytics_tool import (
    get_temperature_trends,
    compare_units,
    compare_recent_units,
    get_system_statistics
)


def create_agent():
    """
    Create and configure the LangGraph agent with API-based tools.
    
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
    
    # Define all tools (now API-based)
    tools = [
        # Unit management tools
        get_unit_metadata,           # Get specific unit details
        list_units,                  # List/search units
        
        # Sensor data tools
        get_sensor_data,             # Get data for specific time range
        get_recent_sensor_data,      # Convenience: get last N days
        
        # Analytics tools
        get_temperature_trends,      # Trend analysis
        compare_units,               # Compare units (specific time range)
        compare_recent_units,        # Compare units (last N days)
        get_system_statistics        # System-wide stats
    ]
    
    # Create ReAct agent with all tools
    agent = create_react_agent(llm, tools)
    
    return agent