import socket
import threading
import paramiko
import datetime

# ==========================================
# CONFIGURATION
# ==========================================
BIND_IP = "0.0.0.0"
BIND_PORT = 2222

# Generate a temporary cryptographic key so attackers think this is a real server
print("[*] Generating cryptographic RSA key... (this takes a second)")
HOST_KEY = paramiko.RSAKey.generate(2048)

# ==========================================
# SSH SERVER LOGIC (THE TRAP)
# ==========================================
class SSH_Honeypot(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.event = threading.Event()

    # Tell the attacker that we require a password to log in
    def get_allowed_auths(self, username):
        return "password"

    # INTERCEPT THE CREDENTIALS
    def check_auth_password(self, username, password):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[🚨 {timestamp}] ATTACK CAPTURED -> IP: {self.client_ip} | User: '{username}' | Pass: '{password}'")
        
        # Always return AUTH_FAILED so they keep trying to brute-force us!
        return paramiko.AUTH_FAILED 

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

# ==========================================
# CONNECTION HANDLER
# ==========================================
def handle_connection(client_socket, client_address):
    ip = client_address[0]
    print(f"\n[>] Incoming connection from {ip}...")
    
    try:
        # Wrap the raw socket in an encrypted Paramiko SSH Transport layer
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)
        
        # Start the fake SSH Server
        server = SSH_Honeypot(client_ip=ip)
        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            print(f"[-] SSH negotiation failed with {ip}.")
            return
            
        # Keep the connection open for 20 seconds to give them time to guess passwords
        channel = transport.accept(20)
        
    except Exception as e:
        print(f"[-] Error handling {ip}: {e}")
    finally:
        try:
            transport.close()
        except:
            pass

# ==========================================
# MAIN SERVER LOOP
# ==========================================
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((BIND_IP, BIND_PORT))
    server_socket.listen(100)
    
    print(f"[*] 🛡️ Cryptographic SSH Honeypot active on Port {BIND_PORT}...")
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            # Start a new thread for every attacker
            threading.Thread(target=handle_connection, args=(client_socket, client_address)).start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down honeypot...")

if __name__ == "__main__":
    start_server()