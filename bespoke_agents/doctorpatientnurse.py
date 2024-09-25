import os
from dotenv import load_dotenv
from autogen import ConversableAgent

# Load environment variables
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("CEREBRAS_API_KEY")

# Create ConversableAgent instances
doctor = ConversableAgent(
    "doctor",
    system_message="You are a doctor conducting an OSCE examination. Your objective is to assess and diagnose a patient presenting with double vision, difficulty climbing stairs, and upper limb weakness.",
    llm_config={
        "config_list": [{
            "model": "llama3.1-70b",
            "api_key": api_key,
            "base_url": "https://api.cerebras.ai/v1",
            "api_type": "openai",
            "temperature": 0.7
        }]
    },
    human_input_mode="NEVER",  # Never ask for human input
)

patient = ConversableAgent(
    "patient",
    system_message="You are a 35-year-old female patient. You have a 1-month history of experiencing double vision (diplopia), difficulty in climbing stairs, and weakness when trying to brush your hair. These symptoms worsen after physical activity but improve significantly after a few hours of rest. You have no significant past medical history, are a non-smoker, drink wine occasionally, and work as a graphic designer.",
    llm_config={
        "config_list": [{
            "model": "llama3.1-70b",
            "api_key": api_key,
            "base_url": "https://api.cerebras.ai/v1",
            "api_type": "openai",
            "temperature": 0.9
        }]
    },
    human_input_mode="NEVER",  # Never ask for human input
)

nurse = ConversableAgent(
    "nurse",
    system_message="You are an intimidating nurse who demands precise answers. After the doctor's diagnosis, you will ask what disease the patient had according to the doctor. Expect and insist on a clear, concise answer.",
    llm_config={
        "config_list": [{
            "model": "llama3.1-70b",
            "api_key": api_key,
            "base_url": "https://api.cerebras.ai/v1",
            "api_type": "openai",
            "temperature": 0.5
        }]
    },
    human_input_mode="NEVER",  # Never ask for human input
)

# Initiate a chat between the doctor and patient
result = doctor.initiate_chat(patient, message="Hello, I understand you're experiencing some health issues. Can you tell me about your symptoms?", max_turns=10)

# Nurse asks for the diagnosis
nurse_result = nurse.initiate_chat(doctor, message="Doctor, what disease did the patient have?", max_turns=2)

# Print the results of the conversations
print("Doctor-Patient Conversation:")
print(result)
print("\nNurse-Doctor Conversation:")
print(nurse_result)