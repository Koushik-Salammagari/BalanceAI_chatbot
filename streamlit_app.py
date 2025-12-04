import streamlit as st
from dotenv import load_dotenv
from agent import create_agent

# Load environment variables
load_dotenv()

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

if "agent" not in st.session_state:
    with st.spinner("Initializing agent..."):
        st.session_state.agent = create_agent()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about sensor data..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Invoke agent
                response = st.session_state.agent.invoke({
                    "messages": [("user", prompt)]
                })
                
                # Extract assistant's response
                assistant_message = response["messages"][-1].content
                
                # Display response
                st.markdown(assistant_message)
                
                # Add to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

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
    - "What's the average temperature in unit 5A?"
    - "Show me data for unit 8C"
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()