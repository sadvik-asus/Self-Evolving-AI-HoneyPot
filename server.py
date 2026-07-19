import asyncio
import asyncssh
import sys
import logging
from db import log_connection, log_interaction
from geoip import get_geo_data
from ai_engine import get_ai_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('HoneypotServer')

class SSHHoneypotServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        self._conn = conn
        self.ip_address = conn.get_extra_info('peername')[0]
        self.port = conn.get_extra_info('peername')[1]
        self.connection_id = -1 # Will be set asynchronously
        logger.info(f"New connection from {self.ip_address}:{self.port}")

    def connection_lost(self, exc):
        logger.info("Connection lost")

    def begin_auth(self, username):
        # We accept any authentication to let the attacker in!
        return False # This means we require password auth, but below we accept any

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        # Accept literally any username/password combination
        logger.info(f"Attacker tried username: '{username}' and password: '{password}'")
        # We should log these credentials too, but for now just let them in
        return True

async def handle_client(process):
    peername = process.get_extra_info('peername')
    if not peername:
        peername = ('Unknown', 0)
    ip_address, port = peername[0], peername[1]
    
    # Perform GeoIP and Database logging asynchronously in a background thread
    def log_initial_connection():
        geo_data = get_geo_data(ip_address)
        return log_connection(ip_address, port, geo_data)
        
    connection_id = await asyncio.to_thread(log_initial_connection)
    logger.info(f"Logged connection ID {connection_id} for {ip_address}")

    # Send a fake welcome message
    process.stdout.write("Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-101-generic x86_64)\n\n")
    process.stdout.write(" * Documentation:  https://help.ubuntu.com\n")
    process.stdout.write(" * Management:     https://landscape.canonical.com\n")
    process.stdout.write(" * Support:        https://ubuntu.com/pro\n\n")
    
    connection_id = getattr(process.channel.get_connection()._server, 'connection_id', -1)
    
    while not process.stdin.at_eof():
        process.stdout.write("root@server:~# ")
        command = await process.stdin.readline()
        if not command:
            break
            
        command = command.strip()
        if not command:
            continue
            
        logger.info(f"Received command: {command}")
        
        if command in ['exit', 'logout']:
            process.stdout.write("logout\n")
            process.exit(0)
            break
            
        # Get AI-generated response based on the command, running in a thread to prevent blocking the async loop
        ai_response = await asyncio.to_thread(get_ai_response, connection_id, command)
        
        # Log to database, also in a thread
        await asyncio.to_thread(log_interaction, connection_id, command, ai_response)
        
        process.stdout.write(ai_response)

async def start_server():
    import os
    key_path = 'server_key'
    if os.path.exists(key_path):
        server_key = asyncssh.read_private_key(key_path)
        logger.info("Loaded existing server key.")
    else:
        server_key = asyncssh.generate_private_key('ssh-rsa')
        server_key.write_private_key(key_path)
        logger.info("Generated and saved new server key.")
    
    await asyncssh.listen('', 8022, server_host_keys=[server_key],
                          server_factory=SSHHoneypotServer,
                          process_factory=handle_client)
    
    logger.info("Honeypot listening on port 8022...")

async def main():
    await start_server()
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (OSError, asyncssh.Error) as exc:
        sys.exit(f'Error starting server: {exc}')
    except KeyboardInterrupt:
        pass
