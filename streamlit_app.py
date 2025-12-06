import streamlit as st
from dotenv import load_dotenv
from agent import create_agent
from utils.error_handler import format_user_error
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="IoT Sensor Chatbot",
    page_icon="🌡️",
    layout="centered"
)

# Title
st.title("🌡️ IoT Sensor Data Chatbot")
st.markdown("Ask questions about temperature and humidity data from your units.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    logger.info("Initialized new chat session")

if "agent" not in st.session_state:
    with st.spinner("Initializing agent..."):
        try:
            st.session_state.agent = create_agent()
            logger.info("Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}", exc_info=True)
            st.error("Failed to initialize chatbot. Please check configuration.")
            st.stop()

# Initialize conversation history for agent
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about sensor data..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    logger.info(f"User query: {prompt}")
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Add user message to agent conversation history
                st.session_state.agent_messages.append(("user", prompt))
                
                # Invoke agent with full conversation history
                response = st.session_state.agent.invoke({
                    "messages": st.session_state.agent_messages
                })
                
                # Extract assistant's response
                assistant_message = response["messages"][-1].content
                
                # Add assistant response to agent conversation history
                st.session_state.agent_messages.append(("assistant", assistant_message))
                
                # Display response
                st.markdown(assistant_message)
                logger.info("Agent response generated successfully")
                
                # Add to display history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
            except KeyError as e:
                error_msg = "⚠️ Error: Unable to process response. Please try again."
                logger.error(f"KeyError in agent response: {str(e)}", exc_info=True)
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
            
            except ValueError as e:
                error_msg = f"⚠️ Invalid input: {str(e)}"
                logger.error(f"ValueError: {str(e)}")
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
            
            except Exception as e:
                error_msg = f"❌ An unexpected error occurred. Please try again or contact support."
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                
                # Show detailed error in expander for debugging
                with st.expander("🔍 Technical Details"):
                    st.code(str(e))

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This chatbot can answer questions about:
    - Temperature data
    - Humidity data
    - Unit information
    - Time-based queries
    
    **Example queries:**
    - "Get temperature stats for unit 12H in apartment 4 on Oct 27 from 2pm to 5pm"
    - "What was the maximum?" (follow-up question)
    - "Show me data for unit 8C"
    
    **💡 Features:**
    - ✅ Conversation memory
    - ✅ Error handling
    - ✅ Logging enabled
    """)
    
    st.divider()
    
    # Show conversation stats
    if st.session_state.agent_messages:
        st.metric("Conversation turns", len(st.session_state.agent_messages) // 2)
    
    # Show system status
    st.subheader("📊 System Status")
    try:
        from pathlib import Path
        from config.settings import DYNAMODB_MOCK_PATH, TIMESTREAM_MOCK_PATH
        
        db_status = "✅" if Path(DYNAMODB_MOCK_PATH).exists() else "❌"
        ts_status = "✅" if Path(TIMESTREAM_MOCK_PATH).exists() else "❌"
        
        st.text(f"DynamoDB: {db_status}")
        st.text(f"Timestream: {ts_status}")
        st.text(f"Agent: ✅")
    except Exception:
        st.text("Status: Unknown")
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.agent_messages = []
        logger.info("Chat history cleared")
        st.rerun()
    
    # Download logs button
    if st.button("📥 Download Logs"):
        try:
            with open('chatbot.log', 'r') as f:
                logs = f.read()
            st.download_button(
                label="Download chatbot.log",
                data=logs,
                file_name="chatbot.log",
                mime="text/plain"
            )
        except FileNotFoundError:
            st.warning("No log file found")