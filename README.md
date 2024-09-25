## TEST AGENTS

To test the agent
```
uv venv agent_env
source agent_env/bin/activate
uv pip install pyautogen 
uv pip install python-dotenv
uv pip install gradio
cd bespoke_agents
touch .env 
```

in .env load 
```
CEREBRAS_API_KEY = ''
```


To sign in to the cerebras platform: https://cloud.cerebras.ai/platform/

Latest file: bespoke_agents/doctorpatientnurse_ui.py