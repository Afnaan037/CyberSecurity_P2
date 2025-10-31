# simulate_keylogger.py — simulates keylogger behavior without capturing real keystrokes
import os, base64, socket
from cryptography.fernet import Fernet
from datetime import datetime

KEY_FILE = "key.key"
LOG_FILE = "keylog.txt"
HOST = "127.0.0.1"
PORT = 4444

def gen_or_load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_and_store_and_send(text):
    key = gen_or_load_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(text.encode("utf-8"))
    payload = base64.b64encode(encrypted)

    # store locally
    with open(LOG_FILE, "ab") as f:
        f.write(payload + b"\\n")
    print("[*] Encrypted log written to " + LOG_FILE)

    # send to server
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(payload)
        print("[*] Sent to server.")
    except Exception as e:
        print("[!] Failed to send to server:", e)

if __name__ == "__main__":
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sample = f"--- Log Entry: {ts} ---\\nSimulated input: hello world\\n"
    encrypt_and_store_and_send(sample)