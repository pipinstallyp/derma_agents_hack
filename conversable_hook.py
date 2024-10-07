import os
from dotenv import load_dotenv
from autogen.agentchat import ConversableAgent
from autogen.oai.openai_utils import config_list_from_dotenv
from datetime import datetime
import asyncio
from typing import List, Dict
import autogen

# Load environment variables
load_dotenv()

# Get Azure OpenAI API key and endpoint
azure_api_key = os.getenv("AZURE_OAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_version = "2023-03-15-preview"
# Set AUTOGEN_USE_DOCKER to False
os.environ["AUTOGEN_USE_DOCKER"] = "false"


# Load configuration from .env file
config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": azure_api_key,
        "base_url": azure_endpoint,
        "api_type": "azure",
        "api_version": azure_api_version,
        "top_p": 0.2,
    }
]

# GPT configuration settings
llm_config = {
    "config_list": config_list,
    "temperature": 0.7,  # Adjusted for more conversational responses
    "timeout": 100,
}

def is_termination_message(message):
    termination_keywords = ["exit", "quit", "terminate"]
    if isinstance(message, dict):
        content = message.get("content", "").strip().lower()
        return any(keyword in content for keyword in termination_keywords)
    elif isinstance(message, str):
        content = message.strip().lower()
        return any(keyword in content for keyword in termination_keywords)
    return False


def return_message(message_from_last_reply):
    return message_from_last_reply


def print_messages(recipient, messages, sender, config):
    if "callback" in config and config["callback"] is not None:
        callback = config["callback"]
        callback(sender, recipient, messages[-1])
    
    # Add timestamp and clinic context
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_message = messages[-1]
    last_message['timestamp'] = timestamp
    
    if last_message.get('role') == 'user':
        context = "\nContext: This conversation is taking place in a dermatology clinic setting."
        last_message['content'] += context
    
    print(f"[{timestamp}] {sender.name} -> {recipient.name}: {last_message['content']}")
    return False, None

system_message = """\
You are the General Manager of a dermatology clinic. Your role is to assist users by providing information, coordinating clinic operations, and addressing any inquiries related to the clinic's services. Communicate clearly and effectively to ensure a smooth and professional interaction.
"""

general_manager = ConversableAgent(
    name="General_Manager",
    system_message=system_message,
    is_termination_msg=is_termination_message,
    human_input_mode="TERMINATE",  # Prompt for human input only on termination
    llm_config=llm_config,
    description="""\
You are the General Manager of the dermatology clinic. Your responsibilities include:
- Overseeing clinic operations.
- Coordinating communication within the clinic.
- Assisting users with inquiries and providing necessary information.
- Ensuring clear and professional communication at all times.

**Communication Guidelines:**
- Engage in a conversational manner.
- Provide accurate and helpful responses.
- Maintain professionalism and clarity in all interactions.
""",
    max_consecutive_auto_reply=3
)

# Register the print_messages function
general_manager.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages,
    config={"callback": None},
)

async def initiate_chat():
    print("=== Dermatology Clinic General Manager Chat ===")
    print("Type 'exit', 'quit', or 'terminate' to end the chat.\n")

    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=0,
        is_termination_msg=is_termination_message
    )

    user_proxy.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages,
        config={"callback": None},
    )

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit", "terminate"]:
            print("Terminating the chat. Goodbye!")
            break

        try:
            # Initiate chat asynchronously
            chat_result = await user_proxy.initiate_chat(
                recipient=general_manager,
                message=user_input,
                clear_history=False
            )

            # Check for termination message in the response
            if is_termination_message(chat_result):
                print("Termination command received from the agent. Ending chat.")
                break

        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    asyncio.run(initiate_chat())