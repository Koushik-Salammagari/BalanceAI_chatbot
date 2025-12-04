import os
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data paths
DYNAMODB_MOCK_PATH = BASE_DIR / "data" / "mock_dynamodb.json"
TIMESTREAM_MOCK_PATH = BASE_DIR / "data" / "mock_timestream.json"

# LLM Configuration
LLM_PROVIDER = "openai" # "anthropic"
LLM_MODEL =  "gpt-5.1" # "claude-3-5-sonnet-20241022"  # or
LLM_TEMPERATURE = 0

# API Keys (from environment variables)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Agent Configuration
MAX_ITERATIONS = 10
VERBOSE = True

# AWS Configuration (for future use)
AWS_REGION = "us-east-1"
DYNAMODB_TABLE_NAME = "units_metadata"
TIMESTREAM_DATABASE = "sensor_data"
TIMESTREAM_TABLE = "readings"