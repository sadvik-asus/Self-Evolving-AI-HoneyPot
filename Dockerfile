FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Initialize the database
RUN python db.py

# Expose the SSH Honeypot port
EXPOSE 8022

# Start the server
CMD ["python", "server.py"]
