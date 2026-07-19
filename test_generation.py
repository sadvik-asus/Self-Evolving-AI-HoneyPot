import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

persona = """You are a vulnerable Ubuntu 22.04 LTS Linux server.
An attacker has gained SSH access to you.
Your goal is to trick the attacker into thinking they are on a real system.
Generate the exact raw terminal output for the command the attacker provides.
Do not provide any explanations, introductory text, or markdown formatting (unless it's part of the raw output).
Just provide the exact text that would appear on the terminal when the command is run.
If a command requires root privileges and they use sudo without a password prompt context, simulate the output of a successful execution.
If a command is not found, output 'bash: command not found' appropriately.
The current user is 'root' and the home directory is '/root'."""

try:
    model = genai.GenerativeModel('gemini-flash-latest', system_instruction=persona)
    chat = model.start_chat()
    response = chat.send_message("Attacker runs command: ls -la")
    print(f"RAW OUTPUT FROM AI (repr): {repr(response.text)}")
except Exception as e:
    print(f"Error: {e}")
