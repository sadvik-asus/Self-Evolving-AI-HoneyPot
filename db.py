import sqlite3
import os
from datetime import datetime

DB_NAME = "honeypot.db"

def init_db():
    """Initializes the SQLite database with the necessary tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Table for storing connection attempts (IP, Port, GeoIP data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            port INTEGER NOT NULL,
            country TEXT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            isp TEXT
        )
    ''')

    # Table for storing the actual commands executed by the attacker and AI responses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            connection_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            command TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            FOREIGN KEY (connection_id) REFERENCES connections (id)
        )
    ''')

    conn.commit()
    conn.close()

def log_connection(ip_address, port, geo_data=None):
    """Logs a new connection and returns the connection ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    timestamp = datetime.utcnow().isoformat()
    
    if geo_data is None:
        geo_data = {}
        
    cursor.execute('''
        INSERT INTO connections (timestamp, ip_address, port, country, city, latitude, longitude, isp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp, 
        ip_address, 
        port, 
        geo_data.get('country'), 
        geo_data.get('city'),
        geo_data.get('lat'), 
        geo_data.get('lon'),
        geo_data.get('isp')
    ))
    
    conn.commit()
    connection_id = cursor.lastrowid
    conn.close()
    return connection_id

def log_interaction(connection_id, command, ai_response):
    """Logs an interaction (command and response)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    timestamp = datetime.utcnow().isoformat()
    
    cursor.execute('''
        INSERT INTO interactions (connection_id, timestamp, command, ai_response)
        VALUES (?, ?, ?, ?)
    ''', (connection_id, timestamp, command, ai_response))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
