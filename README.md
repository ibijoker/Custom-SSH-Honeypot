# 🕸️ Custom Cryptographic SSH Honeypot

As I transition into Detection Engineering and Threat Hunting, I wanted to understand how Threat Actors conduct automated reconnaissance and brute-force attacks against network infrastructure. Instead of just analyzing existing logs, I built a custom SSH honeypot to generate my own threat intelligence.

---

## 📸 Intercepted Attack Traffic
*A live demonstration of the honeypot capturing a simulated brute-force attack from a Kali Linux Virtual Machine.*
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/3d76ed53-455b-4bdc-9559-ed439f752cb2" />


---

## 🚀 The Architecture
Many basic honeypots simply open a port and listen. However, modern botnets will drop the connection if the server doesn't perform a valid cryptographic handshake. 

To solve this, I engineered a Python-based honeypot using the `paramiko` library to emulate a fully functional, RSA-encrypted SSH server.
* **The Trap:** Binds to a port and projects a fake OpenSSH banner to scanners.
* **The Handshake:** Generates a temporary RSA key to successfully complete the SSH cryptographic negotiation.
* **Credential Harvesting:** Intercepts the username and password attempted by the attacker, logs the IP address, and intentionally returns an `AUTH_FAILED` response to keep the attacker guessing and generate more telemetry.

## 🛠️ Skills Demonstrated
* Network Security & TCP/IP Fundamentals
* Deception Technology & Infrastructure Setup
* Python (Paramiko, Socket Programming, Threading)
* Cross-Subnet Virtual Machine Networking

## How to Run Locally
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python honeypot.py`
4. In a separate terminal (or VM), attack it: `ssh root@127.0.0.1 -p 2222`
