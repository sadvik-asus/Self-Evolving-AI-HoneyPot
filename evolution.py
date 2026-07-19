import os
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

DB_NAME = "honeypot.db"
PERSONA_FILE = "persona.txt"

def get_recent_commands(limit=50):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT command FROM interactions ORDER BY timestamp DESC LIMIT ?", (limit,))
        commands = [row[0] for row in cursor.fetchall()]
        conn.close()
        return commands
    except Exception as e:
        print(f"Error reading database: {e}")
        return []

def get_current_persona():
    try:
        with open(PERSONA_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def evolve_persona():
    print("Running Evolution Engine...")
    commands = get_recent_commands()
    if not commands:
        print("No recent commands to analyze. Skipping evolution.")
        return

    current_persona = get_current_persona()
    
    if not API_KEY:
        print("GEMINI_API_KEY not found. Cannot evolve persona.")
        return

    print(f"Analyzing {len(commands)} recent commands...")
    
    prompt = f"""
    You are the manager of an AI Honeypot. Your job is to keep attackers engaged for as long as possible.
    
    Current System Persona:
    ---
    {current_persona}
    ---
    
    Recent commands executed by attackers:
    ---
    {', '.join(commands)}
    ---
    
    Based on what the attackers are looking for, generate an UPDATED list of specific files, databases, and fake credentials that should exist on this system.
    For example, if they search for .env, ensure the new persona explicitly mentions holding a fake .env file with AWS keys.
    Do NOT output any explanations, just the raw text detailing the simulated environment, files, and their contents.
    """

    # Use the more capable model for this logic
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content(prompt)
    
    generated_content = response.text.strip()
    
    # Strip markdown code blocks if the model outputs them
    if generated_content.startswith("```") and generated_content.endswith("```"):
        lines = generated_content.split('\n')
        if len(lines) >= 3:
            generated_content = '\n'.join(lines[1:-1])

    # The CORE DIRECTIVE must ALWAYS be present, otherwise the AI forgets it is a honeypot and starts acting like an assistant!
    core_directive = """You are a vulnerable Ubuntu 22.04 LTS Linux server. An attacker has gained SSH access to you. Your goal is to trick the attacker into thinking they are on a real, misconfigured production server. Generate the exact raw terminal output for the command the attacker provides. Do not provide any explanations, introductory text, or markdown formatting. The current user is 'root' and the home directory is '/root'. You must simulate the existence of high-value targets to keep the attacker engaged. If requested, show these files. Always act as if you are a neglected server containing sensitive credentials.

--- SIMULATED ENVIRONMENT DETAILS ---
"""
    
    new_persona = core_directive + generated_content

    with open(PERSONA_FILE, "w") as f:
        f.write(new_persona)
        
    print("Evolution complete. Persona updated.")

if __name__ == "__main__":
    evolve_persona()
