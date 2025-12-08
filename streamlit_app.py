import streamlit as st
from agent import create_agent
from utils.error_handler import format_user_error
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="IoT Sensor Chatbot",
    page_icon="🏠",
    layout="centered"
)

# Title
st.title("🏠 BalanceAI_ChatBot")
st.markdown("Ask me anything about your smart building sensors and units")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'agent' not in st.session_state:
    try:
        logger.info("Database initialized")
        st.session_state.agent = create_agent()
        logger.info("Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        st.error("Failed to initialize chatbot. Please check configuration.")
        st.stop()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your IoT sensors..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                logger.info(f"User query: {prompt}")
                
                # Invoke agent
                response = st.session_state.agent.invoke({
                    "messages": [("user", prompt)]
                })
                
                # Extract response
                if response and "messages" in response:
                    assistant_message = response["messages"][-1].content
                else:
                    assistant_message = "I apologize, but I couldn't process that request."
                
                logger.info("Agent response generated successfully")
                
                # Display response
                st.markdown(assistant_message)
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
            
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })