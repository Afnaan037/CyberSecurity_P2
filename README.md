Proof-of-Concept Encrypted Keylogger
🚨 Ethical Disclaimer 🚨
This project is a Proof-of-Concept (PoC) created for educational purposes within a controlled cybersecurity internship exercise. It demonstrates concepts of keystroke logging, data encryption, and network data exfiltration.

Using this software on any computer system without the owner's explicit, written permission is illegal and unethical. The author is not responsible for any misuse or damage caused by this program.

Objective
This project fulfills the requirement to build a keylogger that captures keystrokes, encrypts the logged data using a strong cipher, stores the logs locally, and simulates data exfiltration to a remote server. It also includes features for persistence and a kill switch for safe termination.

Features
Keystroke Logging: Captures both alphanumeric and special keys using pynput.

Strong Encryption: Uses the cryptography library with the Fernet (AES-128-CBC) symmetric encryption scheme.

Encrypted Local Logs: Stores logs locally in keylog.txt in an encrypted format.

Timestamping: Each log batch is timestamped.

Simulated Data Exfiltration: Sends encrypted logs over a TCP socket to a listener (server.py) every 10 seconds.

Startup Persistence: Includes a function to add the script to the Windows Registry Run key for persistence across reboots (requires admin rights).

Kill Switch: Pressing the Esc key will safely shut down the keylogger and send any final logs.

Key Management: Automatically generates an encryption key (key.key) on the first run.

How to Run the PoC
1. Prerequisites
You need Python 3 installed. Then, install the required libraries:

pip install pynput cryptography

2. Setup and Execution
The simulation requires two terminal windows.

In Terminal 1 (Start the Server first):

Run the keylogger.py script once to generate the key.key file.

python keylogger.py

You will see a message that a key has been generated. You can close it immediately with Esc.

Now that key.key exists, start the server to listen for incoming logs.

python server.py

The server will confirm it has loaded the key and is listening.

In Terminal 2 (Run the Keylogger):

Run the keylogger script.

python keylogger.py

The script is now running in the background. Start typing in any other application (like a text editor or web browser).

Every 10 seconds, the keylogger will send the captured keystrokes. You will see the encrypted data appear in the server terminal, followed by the decrypted log content.

To stop the keylogger, make sure the keylogger's terminal window is in focus and press the Esc key.

3. Deliverables and Logs
keylogger.py: The main keylogger source code.

server.py: The server source code for receiving and decrypting data.

key.key: The generated symmetric encryption key.

keylog.txt: The local log file containing the encrypted and Base64-encoded keystroke data.

This setup successfully demonstrates the entire lifecycle of the attack vector: capture, encryption, local storage, exfiltration, and decryption on the attacker's machine.
