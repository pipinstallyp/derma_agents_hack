import os
import gradio as gr
from dotenv import load_dotenv
from autogen import ConversableAgent, ChatResult

# Load environment variables
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("CEREBRAS_API_KEY")

def create_agent(name, system_message, temperature):
    return ConversableAgent(
        name,
        system_message=system_message,
        llm_config={
            "config_list": [{
                "model": "llama3.1-70b",
                "api_key": api_key,
                "base_url": "https://api.cerebras.ai/v1",
                "api_type": "openai",
                "temperature": temperature
            }]
        },
        human_input_mode="NEVER",  # Never ask for human input
    )

def run_simulation(doctor_message, patient_message, nurse_message):
    doctor = create_agent("doctor", doctor_message, 0.7)
    patient = create_agent("patient", patient_message, 0.9)
    nurse = create_agent("nurse", nurse_message, 0.5)

    # Initiate a chat between the doctor and patient
    doctor.initiate_chat(patient, message="Hello, I understand you're experiencing some health issues. Can you tell me about your symptoms?", max_turns=10)

    # Nurse asks for the diagnosis
    nurse_result = nurse.initiate_chat(doctor, message="Doctor, what disease did the patient have?", max_turns=2)

    print("The nurse result is: ", nurse_result)

    # Return only the last user message from the nurse_result
    if nurse_result.chat_history:
        for msg in reversed(nurse_result.chat_history):
            if msg['role'] == 'user':
                return msg['content']
    return "Sorry nurse didn't get paid enough to answer ;-;"

# Define the Gradio interface
iface = gr.Interface(
    fn=run_simulation,
    inputs=[
        gr.Textbox(label="Doctor's System Message", 
                   value="You are a doctor conducting an OSCE examination. Your objective is to assess and diagnose a patient presenting with double vision, difficulty climbing stairs, and upper limb weakness."),
        gr.Textbox(label="Patient's System Message", 
                   value="You are a 35-year-old female patient. You have a 1-month history of experiencing double vision (diplopia), difficulty in climbing stairs, and weakness when trying to brush your hair. These symptoms worsen after physical activity but improve significantly after a few hours of rest. You have no significant past medical history, are a non-smoker, drink wine occasionally, and work as a graphic designer."),
        gr.Textbox(label="Nurse's System Message", 
                   value="You are an intimidating nurse who demands precise answers. After the doctor's diagnosis, you will ask what disease the patient had according to the doctor. Expect and insist on a clear, concise answer.")
    ],
    outputs="text",
    title="Medical Diagnosis Simulation",
    description="Enter system messages for the doctor, patient, and nurse to simulate a medical diagnosis scenario."
)

# Launch the interface
iface.launch()