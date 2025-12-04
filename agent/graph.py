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
from tools import query_dynamodb, query_timestream


# Wrap tools with LangChain @tool decorator
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
        unit_id: Unit identifier (e.g., "apt4-12H-002")
        start_time: Start timestamp in ISO format (e.g., "2025-10-27T14:00:00Z")
        end_time: End timestamp in ISO format (e.g., "2025-10-27T17:00:00Z")
    
    Returns:
        Sensor readings with temperature/humidity statistics
    """
    return query_timestream(unit_id, start_time, end_time)


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
    
    # Define tools
    tools = [get_unit_metadata, get_sensor_data]
    
    # Create ReAct agent
    agent = create_react_agent(llm, tools)
    
    return agent