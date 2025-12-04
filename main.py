import os
from dotenv import load_dotenv
from agent import create_agent

# Load environment variables
load_dotenv()


def main():
    """
    Main entry point for the chatbot.
    """
    print("=" * 60)
    print("IoT Sensor Data Chatbot")
    print("=" * 60)
    print("Ask questions about units, temperature, and humidity data.")
    print("Type 'exit' or 'quit' to end the conversation.\n")
    
    # Create agent
    agent = create_agent()
    
    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            # Invoke agent
            response = agent.invoke({
                "messages": [("user", user_input)]
            })
            
            # Extract assistant's final message
            assistant_message = response["messages"][-1].content
            
            print(f"\nAssistant: {assistant_message}\n")
            print("-" * 60 + "\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    main()