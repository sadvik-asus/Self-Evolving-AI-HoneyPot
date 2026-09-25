import asyncio
import asyncssh
import sys
import traceback

class SSHHoneypotServer(asyncssh.SSHServer):
    def begin_auth(self, username):
        return False
    def password_auth_supported(self):
        return True
    def validate_password(self, username, password):
        return True

async def handle_client(process):
    try:
        # Let's see if we can get peername
        peername = process.get_extra_info('peername')
        ip_address = peername[0]
        
        process.stdout.write("Welcome!\n")
        
        server = process.channel.get_connection()._server
        process.stdout.write(f"Server class: {type(server)}\n")
        
    except Exception as e:
        with open("error.log", "w") as f:
            f.write(traceback.format_exc())
        process.exit(1)

async def start_server():
    server_key = asyncssh.generate_private_key('ssh-rsa')
    await asyncssh.listen('', 8023, server_host_keys=[server_key],
                          server_factory=SSHHoneypotServer,
                          process_factory=handle_client)
    print("Listening on 8023")

async def test_client():
    await asyncio.sleep(1) # wait for server
    try:
        async with asyncssh.connect('localhost', port=8023, username='root', password='pw', known_hosts=None) as conn:
            result = await conn.run('ls', check=True)
            print("Output:", result.stdout)
    except Exception as e:
        print("Client error:", e)

async def main():
    server_task = asyncio.create_task(start_server())
    await test_client()
    server_task.cancel()

asyncio.run(main())
