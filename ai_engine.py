import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Warning: GEMINI_API_KEY not found in .env file.")
else:
    genai.configure(api_key=API_KEY)

def get_system_prompt():
    try:
        with open("persona.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a vulnerable Ubuntu 22.04 LTS Linux server. Generate raw terminal output."

# We need to disable safety blocks because attackers will run malicious commands
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}
]

# Initialize the model with the system instruction
try:
    model = genai.GenerativeModel('gemini-flash-lite-latest', system_instruction=get_system_prompt(), safety_settings=SAFETY_SETTINGS)
except AttributeError:
    model = genai.GenerativeModel('gemini-flash-lite-latest', safety_settings=SAFETY_SETTINGS)

# Maintain conversation history per connection
chat_sessions = {}

def get_ai_response(connection_id, command):
    """
    Takes the connection ID and the attacker's command, sends it to Gemini, 
    and returns the hallucinated terminal output.
    """
    if not API_KEY:
        return f"bash: {command}: command not found\n"
        
    if connection_id not in chat_sessions:
        # Update the model's system instruction dynamically if possible, or just create a new chat
        # For simplicity, if they want a fresh session with updated persona, they get a new chat.
        current_persona = get_system_prompt()
        try:
            model = genai.GenerativeModel('gemini-flash-lite-latest', system_instruction=current_persona, safety_settings=SAFETY_SETTINGS)
        except AttributeError:
            pass # Fallback

        # Start a new chat session for this connection
        chat_sessions[connection_id] = model.start_chat(history=[])
        
    chat = chat_sessions[connection_id]
    
    try:
        # Some SDK versions require system prompt to be passed in differently if not supported above.
        # But we assume the modern SDK supports system_instruction.
        response = chat.send_message(f"Attacker runs command: {command}")
        
        # Ensure we return plain text without markdown code blocks if the model accidentally adds them
        output = response.text.strip()
        if output.startswith("```") and output.endswith("```"):
            lines = output.split('\n')
            if len(lines) >= 3:
                output = '\n'.join(lines[1:-1])
                
        return output + "\n"
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return f"bash: {command}: input/output error\n"

if __name__ == "__main__":
    # Simple local test
    print(get_ai_response(1, "ls -la /"))
