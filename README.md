# AI-Powered SSH Honeypot

This is a dynamic, AI-powered SSH honeypot that tricks attackers into thinking they have compromised a real production server. It hallucinates a fake Linux environment (Ubuntu 22.04), responds to bash commands in real-time using Google Gemini, and logs all attacker activity into a beautifully designed Sci-Fi Web Dashboard.

## Features
- **Dynamic Persona:** The server hallucinates realistic files like `.env` and `passwords.txt` based on what attackers are searching for.
- **Sci-Fi Web Dashboard:** Watch attacks happen in real-time on a global map and a live threat feed.
- **Evolution Engine:** The honeypot analyzes recent attacks and evolves its persona to bait future hackers even better.

## Prerequisites
- Python 3.9+
- A Google Gemini API Key

## Setup & Installation

1. **Extract the ZIP file** to a folder on your computer.
2. **Open a terminal/command prompt** in that folder.
3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
4. **Activate the virtual environment:**
   - **Windows:** `.\venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`
5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
6. **Set up your API Key:**
   - Open the `.env` file (create it if it doesn't exist).
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY="your_api_key_here"
     ```

## How to Run Locally

You need to run two scripts simultaneously in two separate terminals (make sure the virtual environment is activated in both).

**Terminal 1 (Start the SSH Server):**
```bash
python server.py
```

**Terminal 2 (Start the Web Dashboard):**
```bash
python web_app.py
```

Now, open your web browser and go to `http://localhost:5000` to view the dashboard!

## How to Test the Honeypot
Open a third terminal and pretend to be a hacker:
```bash
ssh root@localhost -p 8022
```
(You can use any password you want, the honeypot will let you in!)
Try typing `ls -la`, `whoami`, or `cat .env` and watch the AI hallucinate the responses while the dashboard logs your every move.
