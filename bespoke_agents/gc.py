import os
from dotenv import load_dotenv
import autogen

# Load environment variables
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("CEREBRAS_API_KEY")

# Set AUTOGEN_USE_DOCKER environment variable
os.environ["AUTOGEN_USE_DOCKER"] = "0"

# Define the configuration for the LLM
config_list = [{
    "model": "llama3.1-70b",
    "api_key": api_key,
    "base_url": "https://api.cerebras.ai/v1",
    "api_type": "openai",
}]

llm_config = {"config_list": config_list, "cache_seed": 42}

# Create agents
user_proxy = autogen.UserProxyAgent(
    name="User",
    system_message="A human patient with a skin problem.",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=0
)

manager = autogen.AssistantAgent(
    name="",
    system_message="You are the chat manager facilitating the conversation between the user and the doctor. Your role is to simplify the interaction, handle user inputs, request clarifications when necessary, consult the doctor, and present the final report to the user.",
    llm_config=llm_config,
)

doctor = autogen.AssistantAgent(
    name="Doctor",
    system_message="You are a dermatologist. Your role is to diagnose skin conditions and provide appropriate prescriptions based on the information provided by the user.",
    llm_config=llm_config,
)

# Set up the group chat
groupchat = autogen.GroupChat(
    agents=[user_proxy, manager, doctor],
    messages=[],
    max_round=2
)
manager_chat = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Get user input
user_message = input("Please describe your skin problem: ")

# User sends initial message
user_proxy.initiate_chat(
    manager_chat,
    message=user_message
)

# Manager processes the user's message and consults the doctor
manager.initiate_chat(
    manager_chat,
    message=f"User has reported the following symptoms: {user_message}. Please provide a diagnosis and possible treatments. PLS let us know if clarification is needed."
)

print("Printing doctor's last message content:")
doctor_last_message = manager.chat_messages[manager_chat][-1]
if doctor_last_message['name'] == 'Doctor':
    print(doctor_last_message['content'])
else:
    print("No message from the doctor found in the last interaction.")
# for attr in dir(generate_oai_reply):
#     if not attr.startswith('__'):
#         print(f"{attr}: {getattr(generate_oai_reply, attr)}")
# Extract doctor's response
#doctor_response = manager.get_agent_response("Doctor")
if doctor_last_message['name'] == 'Doctor':
    doctor_response = doctor_last_message['content']
else:
    print("No message from the doctor found in the last interaction.")

# If clarification is needed
if "clarification needed" in doctor_response.lower():
    clarification = input("The doctor needs more information. Please provide additional details: ")
    user_proxy.send(
        clarification,
        manager_chat
    )
    manager.initiate_chat(
        manager_chat,
        message=f"User has provided additional information: {clarification}. Please update the diagnosis and treatment plan."
    )
    doctor_response = manager.get_agent_response("Doctor")

# Present final report to the user
manager.send(
    f"The doctor has provided the following diagnosis and treatment plan: {doctor_response}",
    manager_chat
)

# Print the results of the conversation
print("The manager is: ")
print(manager)

# To inspect the contents of the manager object
print("\nManager attributes:")
for attr in dir(manager):
    if not attr.startswith('__'):
        print(f"{attr}: {getattr(manager, attr)}")
# Print the chat messages for the UserProxyAgent

print("-------------------------------------------------------------------------------------------------------------")
print("\nChat messages for UserProxyAgent:")
for message in manager.chat_messages[user_proxy]:
    print(f"Role: {message.get('role', 'N/A')}")
    print(f"Content: {message.get('content', 'N/A')}")
print("---")

