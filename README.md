# Image-Based Authentication System using Steganography and PSO

A secure authentication system that uses image steganography and Particle Swarm Optimization (PSO) to embed encrypted passwords within images. The system offers GUI-based signup/login features with AES-based encryption and hashed password storage.

## 🔒 Features
- Embeds encrypted passwords in images using LSB steganography
- Uses Particle Swarm Optimization to reduce image distortion
- GUI for signup/login with image selection
- AES encryption for secure position storage
- PBKDF2 password hashing with salt
- Secure password verification on login

## 🧠 Tech Stack
- Python
- OpenCV
- Tkinter
- Cryptography (Fernet, PBKDF2)
- PSO algorithm
- PIL (Pillow)

## 🗂 Files
- `stegoPso4.py`: GUI-based full app
- `L_stegoPso4.py`: Logic-heavy version (optional/backup)
- `auth_data.json`: Stores usernames and hashed passwords
- `encryption_key.key`: Key file for encrypting position data

## 🚀 How to Run

1. Install dependencies:
   ```bash
   pip install opencv-python pillow cryptography
2. Run the application:
   ```bash
    python stegoPso4.py

3. Use the GUI to:
    -> Register: enter username + password, select an image.
    -> Login: select your stego image and validate access.

⚠️ **Note:** This application currently supports **.png images only** for password embedding and retrieval.

## 🖼 Example
-> During signup, password is embedded in the image using steganography.
-> Encrypted pixel positions are saved in a .enc file.
-> At login, system extracts password from the image and verifies it securely.

## 🙌 Credits

This project was developed as part of a group submission at KIIT University.

**Team Members**  
- Aditya Vishal – Steganographic Embedding Specialist  
- Komma Pallavi – Password Extraction & Recovery Engineer  
- Pintu Kumar – Encryption & Security Specialist  
- Pratyay Patra – Project Lead and UI Developer  
- K. Prahit Ponnada – System Integration & Debugging Engineer (ME)

**Supervisor**  
- Prasenjit Maiti  
