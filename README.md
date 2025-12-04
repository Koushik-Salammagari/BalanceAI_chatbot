# IoT Sensor Data Chatbot

LangGraph-powered chatbot for querying temperature and humidity sensor data from units.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
# OR
OPENAI_API_KEY=your_openai_key_here
```

3. Run the chatbot:
```bash
python main.py
```

## Example Queries

- "Get me the temperature and humidity stats of unit 12H in apartment 4 for October 27th 2025 from 2pm to 5pm"
- "What's the average temperature in unit 5A?"
- "Show me sensor data for unit 12H between 2pm and 5pm on Oct 27"

## Project Structure
```
├── data/              # Mock data files
├── tools/             # Tool functions
├── agent/             # LangGraph agent
├── config/            # Configuration
└── main.py            # Entry point
```

## Notes

- Currently uses mock JSON data
- AWS integration (DynamoDB/Timestream) coming next