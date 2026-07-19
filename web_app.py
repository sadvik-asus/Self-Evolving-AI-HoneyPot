import sqlite3
import os
import asyncio
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ai_engine import get_ai_response
from db import DB_NAME, log_interaction
from evolution import evolve_persona

app = Flask(__name__)
CORS(app)

# Helper function to query the database
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(query, args)
        rv = cur.fetchall()
    except Exception as e:
        print(f"DB Error: {e}")
        rv = []
    finally:
        conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('index.html', client_ip=request.remote_addr)

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    # Fetch recent connections (to show on map and feed)
    connections = query_db('SELECT * FROM connections ORDER BY timestamp DESC LIMIT 10')
    conn_list = []
    
    # Provide mock coordinates for local demo tests so the map always looks cool
    import random
    for ix in connections:
        conn = dict(ix)
        if not conn.get('latitude') or not conn.get('longitude'):
            # Randomly assign a 'hacker' location (e.g., somewhere in Eastern Europe or Asia) for demo
            conn['latitude'] = random.uniform(35.0, 60.0)
            conn['longitude'] = random.uniform(10.0, 110.0)
            conn['city'] = 'Mock Demo Location'
            conn['country'] = 'Unknown'
        conn_list.append(conn)

    # Fetch recent interactions (to show what hackers are typing)
    interactions = query_db('''
        SELECT i.timestamp, i.command, i.ai_response, c.ip_address, c.country 
        FROM interactions i 
        JOIN connections c ON i.connection_id = c.id 
        ORDER BY i.timestamp DESC LIMIT 20
    ''')
    interact_list = [dict(ix) for ix in interactions]

    # Fetch current persona
    persona = ""
    try:
        with open("persona.txt", "r") as f:
            persona = f.read().strip()
    except FileNotFoundError:
        persona = "No persona file found."

    return jsonify({
        "connections": conn_list,
        "interactions": interact_list,
        "persona": persona
    })

@app.route('/api/terminal', methods=['POST'])
def terminal_command():
    data = request.json
    command = data.get('command', '')
    
    client_ip = request.remote_addr
    
    # Check if we already logged a connection for this web user
    conn = query_db('SELECT id FROM connections WHERE ip_address = ? AND port = 80', [client_ip], one=True)
    if not conn:
        from db import log_connection
        import random
        # Give them mock coordinates so they show up on the map!
        mock_geo = {
            'lat': random.uniform(35.0, 60.0),
            'lon': random.uniform(10.0, 110.0),
            'country': 'Web User',
            'city': 'Browser'
        }
        connection_id = log_connection(client_ip, 80, mock_geo)
    else:
        connection_id = conn['id']
    
    # Pass to Gemini to generate the hallucinated response
    response_text = get_ai_response(connection_id, command)
    
    # Log the interaction so it appears in the defender dashboard
    log_interaction(connection_id, command, response_text)
    
    return jsonify({"output": response_text})

@app.route('/api/evolve', methods=['POST'])
def trigger_evolution():
    # Triggers the AI to rewrite its persona based on recent commands
    try:
        evolve_persona()
        return jsonify({"status": "success", "message": "Evolution complete. Persona updated."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Ensure static and templates folders exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Run the web server
    print("Starting Web Dashboard on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
