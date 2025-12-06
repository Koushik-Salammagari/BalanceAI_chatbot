# IoT Sensor Data Chatbot

A production-ready LangGraph-powered chatbot for querying temperature and humidity sensor data from residential units. Features conversational AI, persistent storage, advanced analytics, and multi-unit comparisons.

## 🌟 Features

### Core Capabilities
- ✅ **Natural Language Queries** - Ask questions in plain English
- ✅ **Multi-Database Integration** - Queries DynamoDB (metadata) and Timestream (sensor data)
- ✅ **Conversation Memory** - Remembers context within chat sessions
- ✅ **Persistent Storage** - SQLite database saves all conversations
- ✅ **Advanced Analytics** - Trends, comparisons, date ranges, aggregations
- ✅ **Error Handling** - Graceful failures with user-friendly messages
- ✅ **Logging** - Comprehensive logging for debugging and monitoring

### Query Capabilities

#### Basic Queries
- Get temperature/humidity for specific units and time ranges
- View unit metadata (resident, building, floor, type)
- List all units in an apartment/building

#### Advanced Queries
- **Date Ranges**: "Get data for the last 7 days"
- **Comparisons**: "Compare unit 12H and 5A"
- **Trends**: "What's the temperature trend for unit 12H?"
- **System Stats**: "How many total apartments?"
- **Aggregations**: Daily averages, min/max values

## 🏗️ Architecture
```
User → Streamlit UI → LangGraph Agent → Tools → Mock Data (JSON)
                                              ↓
                                         SQLite DB (Conversations)
```

### Components

1. **Streamlit Frontend** (`streamlit_app.py`)
   - Chat interface
   - Conversation management
   - Search functionality
   - Sidebar with recent chats

2. **LangGraph Agent** (`agent/`)
   - Orchestrates tool calls
   - Maintains conversation context
   - Synthesizes responses

3. **Tools** (`tools/`)
   - `query_dynamodb` - Unit metadata queries
   - `query_timestream` - Sensor data queries
   - `get_units_in_apartment` - List units
   - `query_date_range` - Last N days data
   - `compare_units` - Multi-unit comparison
   - `analyze_trend` - Trend analysis
   - `get_system_stats` - System-wide statistics

4. **Database** (`database/`)
   - SQLite for conversation persistence
   - Search, load, delete conversations

5. **Utils** (`utils/`)
   - Error handling
   - Logging configuration

## 📁 Project Structure
```
BalanceAI/
├── agent/
│   ├── __init__.py
│   ├── graph.py          # LangGraph agent setup
│   └── state.py          # Agent state schema
├── config/
│   └── settings.py       # Configuration settings
├── data/
│   ├── mock_dynamodb.json    # Unit metadata (mock)
│   └── mock_timestream.json  # Sensor readings (mock)
├── database/
│   ├── __init__.py
│   └── db_manager.py     # SQLite conversation storage
├── tools/
│   ├── __init__.py
│   ├── dynamodb_tool.py      # DynamoDB queries
│   ├── timestream_tool.py    # Timestream queries
│   └── advanced_queries.py   # Advanced analytics
├── utils/
│   ├── __init__.py
│   └── error_handler.py  # Error handling & logging
├── main.py               # CLI interface
├── streamlit_app.py      # Web UI
├── requirements.txt
├── .env                  # API keys (not in git)
├── .gitignore
└── README.md
```

## 🚀 Setup

### Prerequisites
- Python 3.11+
- Anthropic API key (or OpenAI API key)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Koushik-Salammagari/BalanceAI_chatbot.git
cd BalanceAI_chatbot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

4. **Run the application**

**Web Interface (Recommended):**
```bash
streamlit run streamlit_app.py
```

**CLI Interface:**
```bash
python main.py
```

## 💬 Example Queries

### Basic Queries
```
Get temperature and humidity stats of unit 12H in apartment 4 for October 27th 2025 from 2pm to 5pm
```

### System Information
```
How many apartments are in the system?
Show me all units in apartment 4
```

### Date Ranges
```
Get temperature data for unit 12H for the last 7 days
Show me recent data for unit 5A
```

### Comparisons
```
Compare unit 12H and unit 5A in apartment 1
Which unit is warmer, 12H or 14J?
```

### Trend Analysis
```
What's the temperature trend for unit 12H over the last week?
Is humidity increasing in unit 5A?
```

### Follow-up Questions (Conversation Memory)
```
User: Get temperature for unit 12H for last week
Bot: [Returns data]
User: What was the maximum?
Bot: The maximum was 26.5°C
```

## 🛠️ Configuration

### LLM Settings (`config/settings.py`)
```python
LLM_PROVIDER = "anthropic"  # or "openai"
LLM_MODEL = "claude-3-5-sonnet-20241022"  # or "gpt-4"
LLM_TEMPERATURE = 0
```

### Mock Data Paths
- DynamoDB: `data/mock_dynamodb.json`
- Timestream: `data/mock_timestream.json`

### Database
- SQLite: `conversations.db` (auto-created)
- Logs: `chatbot.log`

## 🔧 Development

### Current Implementation
- **Data Source**: Mock JSON files
- **Deployment**: Local development
- **Database**: SQLite

### Production Roadmap

#### Phase 1: AWS Integration ⏳
- [ ] Replace mock JSON with boto3
- [ ] Connect to real DynamoDB
- [ ] Connect to real Timestream
- [ ] IAM read-only permissions

#### Phase 2: Deployment 🔜
- [ ] Deploy Streamlit to EC2/ECS
- [ ] Optional: Lambda backend
- [ ] API Gateway setup
- [ ] CloudWatch monitoring

#### Phase 3: Advanced Features 🔜
- [ ] Export to CSV/Excel
- [ ] PDF report generation
- [ ] Charts and visualizations
- [ ] Email notifications
- [ ] Advanced agentic workflows

## 🧪 Testing

**Test the chatbot:**
```bash
streamlit run streamlit_app.py
```

**Test queries:**
1. System stats: "How many apartments?"
2. Date range: "Last 7 days for unit 12H"
3. Comparison: "Compare unit 12H and 5A"
4. Trend: "Temperature trend for unit 12H"

## 📊 Mock Data

### DynamoDB (9 units across 4 apartments)
- Apartment 1: 3 units (North Tower)
- Apartment 2: 2 units (East Tower)
- Apartment 3: 1 unit (West Tower)
- Apartment 4: 3 units (South Tower)

### Timestream (Sensor Data)
- 7 days of data (Nov 28 - Dec 4, 2025)
- 4 readings per day per unit
- Temperature: 19°C - 27°C
- Humidity: 40% - 58%

## 🔐 Security

- API keys stored in `.env` (not in git)
- Read-only database operations
- Error messages sanitized for users
- Comprehensive logging for auditing

## 📝 Logging

Logs are stored in `chatbot.log`:
- User queries
- Tool executions
- Errors and exceptions
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License

## 🙋 Support

For issues or questions, please open an issue on GitHub.

## 🎯 Future Enhancements

- Real-time sensor data streaming
- Multi-language support
- Voice interface
- Mobile app
- Advanced visualizations
- Predictive analytics
- Anomaly detection
- Custom alerts and notifications

## 🏆 Credits

Built with:
- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Streamlit](https://streamlit.io/)
- [Anthropic Claude](https://www.anthropic.com/)

---

**Status**: ✅ Development Complete | ⏳ AWS Integration Pending | 🚀 Production Ready (with mock data)