import streamlit as st
from dotenv import load_dotenv
from agent import create_agent
from utils.error_handler import format_user_error
from database import ConversationDB
import logging
from datetime import datetime

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
    layout="wide"
)

# Initialize database
if "db" not in st.session_state:
    st.session_state.db = ConversationDB()
    logger.info("Database initialized")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "agent" not in st.session_state:
    with st.spinner("Initializing agent..."):
        try:
            st.session_state.agent = create_agent()
            logger.info("Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}", exc_info=True)
            st.error("Failed to initialize chatbot. Please check configuration.")
            st.stop()

# Sidebar
with st.sidebar:
    st.header("💬 Conversations")
    
    # New conversation button
    if st.button("➕ New Conversation", use_container_width=True):
        # Save current conversation if exists
        if st.session_state.current_conversation_id and st.session_state.messages:
            logger.info(f"Saving conversation {st.session_state.current_conversation_id}")
        
        # Reset for new conversation
        st.session_state.messages = []
        st.session_state.agent_messages = []
        st.session_state.current_conversation_id = None
        logger.info("Started new conversation")
        st.rerun()
    
    st.divider()
    
    # List recent conversations
    st.subheader("Recent Chats")
    conversations = st.session_state.db.list_conversations(limit=10)
    
    if conversations:
        for conv in conversations:
            # Format updated time
            updated = datetime.fromisoformat(conv['updated_at'])
            time_str = updated.strftime("%b %d, %I:%M %p")
            
            col1, col2 = st.columns([4, 1])
            with col1:
                # Load conversation button
                if st.button(
                    f"📝 {conv['title'][:30]}...",
                    key=f"load_{conv['conversation_id']}",
                    help=f"{conv['message_count']} messages • {time_str}"
                ):
                    # Load conversation
                    loaded_conv = st.session_state.db.get_conversation(conv['conversation_id'])
                    if loaded_conv:
                        st.session_state.current_conversation_id = conv['conversation_id']
                        st.session_state.messages = [
                            {"role": msg["role"], "content": msg["content"]}
                            for msg in loaded_conv["messages"]
                        ]
                        st.session_state.agent_messages = [
                            (msg["role"], msg["content"])
                            for msg in loaded_conv["messages"]
                        ]
                        logger.info(f"Loaded conversation {conv['conversation_id']}")
                        st.rerun()
            
            with col2:
                # Delete button
                if st.button("🗑️", key=f"del_{conv['conversation_id']}"):
                    st.session_state.db.delete_conversation(conv['conversation_id'])
                    logger.info(f"Deleted conversation {conv['conversation_id']}")
                    st.rerun()
        
    else:
        st.info("No saved conversations yet")
    
    st.divider()
    
    # Search conversations
    st.subheader("🔍 Search")
    search_query = st.text_input("Search in conversations", key="search_input")
    if search_query:
        results = st.session_state.db.search_conversations(search_query)
        if results:
            st.write(f"Found {len(results)} results:")
            for result in results:
                if st.button(
                    f"📄 {result['title'][:25]}...",
                    key=f"search_{result['conversation_id']}"
                ):
                    loaded_conv = st.session_state.db.get_conversation(result['conversation_id'])
                    if loaded_conv:
                        st.session_state.current_conversation_id = result['conversation_id']
                        st.session_state.messages = [
                            {"role": msg["role"], "content": msg["content"]}
                            for msg in loaded_conv["messages"]
                        ]
                        st.session_state.agent_messages = [
                            (msg["role"], msg["content"])
                            for msg in loaded_conv["messages"]
                        ]
                        st.rerun()
        else:
            st.write("No results found")
    
    st.divider()
    
    # System info
    st.subheader("ℹ️ About")
    st.markdown("""
    **Features:**
    - ✅ Conversation memory
    - ✅ Persistent storage
    - ✅ Search history
    - ✅ Enhanced queries
    
    **Example queries:**
    - List all units in apartment 4
    - Compare unit 12H and 5A
    - Temperature trend for last week
    """)

# Main chat area
st.title("🌡️ IoT Sensor Data Chatbot")

# Display current conversation title
if st.session_state.current_conversation_id:
    conv_data = st.session_state.db.get_conversation(st.session_state.current_conversation_id)
    if conv_data:
        st.caption(f"💬 {conv_data['title']}")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about sensor data..."):
    # Create new conversation if needed
    if not st.session_state.current_conversation_id:
        # Generate title from first message (truncated)
        title = prompt[:50] if len(prompt) <= 50 else prompt[:47] + "..."
        st.session_state.current_conversation_id = st.session_state.db.create_conversation(
            title=title
        )
        logger.info(f"Created new conversation {st.session_state.current_conversation_id}")
    
    # Add user message to display and database
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.db.add_message(
        st.session_state.current_conversation_id,
        "user",
        prompt
    )
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
                
                # Add to display history and database
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                st.session_state.db.add_message(
                    st.session_state.current_conversation_id,
                    "assistant",
                    assistant_message
                )
                
            except KeyError as e:
                error_msg = "⚠️ Error: Unable to process response. Please try again."
                logger.error(f"KeyError in agent response: {str(e)}", exc_info=True)
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.session_state.db.add_message(
                    st.session_state.current_conversation_id,
                    "assistant",
                    error_msg
                )
            
            except ValueError as e:
                error_msg = f"⚠️ Invalid input: {str(e)}"
                logger.error(f"ValueError: {str(e)}")
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.session_state.db.add_message(
                    st.session_state.current_conversation_id,
                    "assistant",
                    error_msg
                )
            
            except Exception as e:
                error_msg = f"❌ An unexpected error occurred. Please try again."
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.session_state.db.add_message(
                    st.session_state.current_conversation_id,
                    "assistant",
                    error_msg
                )
                
                # Show detailed error in expander
                with st.expander("🔍 Technical Details"):
                    st.code(str(e))