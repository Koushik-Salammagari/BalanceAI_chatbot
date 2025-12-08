import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data paths
# DYNAMODB_MOCK_PATH = BASE_DIR / "data" / "mock_dynamodb.json"
# TIMESTREAM_MOCK_PATH = BASE_DIR / "data" / "mock_timestream.json"

# NEW: API Gateway settings
#API_BASE_URL = "https://2run5ofd1j.execute-api.us-east-2.amazonaws.com/prod"
API_BASE_URL = "https://2run5ofd1j.execute-api.us-east-2.amazonaws.com/prod"
API_GATEWAY_KEY = os.getenv("API_GATEWAY_KEY")  # ← ADD THIS LINE

# LLM Configuration
LLM_PROVIDER = "openai" # "anthropic"
LLM_MODEL =  "gpt-4o" # "claude-3-5-sonnet-20241022"  # or
LLM_TEMPERATURE = 0

# API Keys (from environment variables)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Agent Configuration
MAX_ITERATIONS = 10
VERBOSE = True

# # AWS Configuration (for future use)
# AWS_REGION = "us-east-1"
# DYNAMODB_TABLE_NAME = "units_metadata"
# TIMESTREAM_DATABASE = "sensor_data"
# TIMESTREAM_TABLE = "readings"

# Logging
LOG_LEVEL = "INFO"