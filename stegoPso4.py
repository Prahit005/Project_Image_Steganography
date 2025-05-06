import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import random
import os
from PIL import Image, ImageTk
import hashlib
import base64
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# PSO Parameters
NUM_PARTICLES = 20
ITERATIONS = 50
AUTH_FILE = "auth_data.json"
SALT_SIZE = 16  # For password hashing
KEY_FILE = "encryption_key.key"  # File to store the encryption key

def generate_encryption_key():
    """Generate and save an encryption key for positions file."""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

def get_fernet():
    """Get a Fernet instance with the encryption key."""
    key = generate_encryption_key()
    return Fernet(key)

def hash_password(password, salt=None):
    """Hash a password with salt using PBKDF2."""
    if salt is None:
        salt = secrets.token_bytes(SALT_SIZE)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    password_hash = kdf.derive(password.encode())
    
    # Encode both salt and hash for storage
    return base64.b64encode(salt).decode() + ":" + base64.b64encode(password_hash).decode()

def verify_password(stored_password, provided_password):
    """Verify a password against its stored hash."""
    salt_str, hash_str = stored_password.split(":")
    salt = base64.b64decode(salt_str)
    
    # Hash the provided password with the same salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    provided_hash = kdf.derive(provided_password.encode())
    
    # Compare the hashes
    stored_hash = base64.b64decode(hash_str)
    return secrets.compare_digest(provided_hash, stored_hash)

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary_data):
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    return ''.join(chr(int(char, 2)) for char in chars if char != '11111111')

def fitness_function(image, positions, binary_data):
    difference = 0
    for i, pos in enumerate(positions):
        if i < len(binary_data):
            pixel_value = int(image.flat[pos])
            new_pixel_value = (pixel_value & 0xFE) | int(binary_data[i])
            difference += abs(pixel_value - new_pixel_value)
    return difference

def pso_optimize(image, binary_data):
    height, width, channels = image.shape
    image_size = height * width * channels

    if len(binary_data) > image_size:
        raise ValueError("Not enough pixels in the image to store the password!")

    particles = [random.sample(range(image_size), min(len(binary_data), image_size)) for _ in range(NUM_PARTICLES)]
    velocities = [random.choices(range(-5, 6), k=min(len(binary_data), image_size)) for _ in range(NUM_PARTICLES)]
    personal_best = particles[:]
    global_best = min(personal_best, key=lambda p: fitness_function(image, p, binary_data))

    for _ in range(ITERATIONS):
        for i in range(NUM_PARTICLES):
            new_positions = [(p + v) % image_size for p, v in zip(particles[i], velocities[i])]
            if fitness_function(image, new_positions, binary_data) < fitness_function(image, personal_best[i], binary_data):
                personal_best[i] = new_positions
            if fitness_function(image, personal_best[i], binary_data) < fitness_function(image, global_best, binary_data):
                global_best = personal_best[i]

    return global_best

def save_auth_data(username, password):
    auth_data = load_auth_data()
    # Store the hashed password instead of plaintext
    auth_data[username] = hash_password(password)
    with open(AUTH_FILE, "w") as f:
        json.dump(auth_data, f)

def load_auth_data():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            return json.load(f)
    return {}

def create_styled_button(parent, text, command, width=15):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg="#f15b50",
        fg="white",
        activebackground="#e04a40",
        activeforeground="white",
        font=("Arial", 11),
        relief=tk.FLAT,
        padx=10,
        pady=8,
        width=width,
        cursor="hand2"
    )
    return button

def create_styled_entry(parent, show=None, width=35):
    entry = tk.Entry(
        parent,
        font=("Arial", 11),
        bd=2,
        relief=tk.SOLID,
        width=width,
        show=show
    )
    return entry

def create_styled_label(parent, text, size=11, bold=False):
    font_weight = "bold" if bold else "normal"
    label = tk.Label(
        parent,
        text=text,
        font=("Arial", size, font_weight),
        anchor="w"
    )
    return label

def create_styled_checkbox(parent, text):
    var = tk.BooleanVar()
    checkbox = tk.Checkbutton(
        parent,
        text=text,
        variable=var,
        font=("Arial", 10),
        anchor="w"
    )
    return checkbox, var

def create_styled_window(title, width=400, height=450):
    window = tk.Toplevel(root)
    window.title(title)
    window.geometry(f"{width}x{height}")
    window.configure(bg="white")
    
    # Center the window
    window.update_idletasks()
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry(f"+{x}+{y}")
    
    frame = tk.Frame(window, bg="white", padx=30, pady=30)
    frame.pack(fill=tk.BOTH, expand=True)
    
    return window, frame

def signup():
    username = username_entry.get().strip()
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg")])

    if not username:
        messagebox.showerror("Error", "Please enter a username.", parent=signup_window)
        return

    if not image_path:
        return

    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Please enter a password.", parent=signup_window)
        return

    img = cv2.imread(image_path)
    binary_data = text_to_binary(password) + '1111111111111110'

    try:
        positions = pso_optimize(img, binary_data)
    except ValueError as e:
        messagebox.showerror("Error", str(e), parent=signup_window)
        return

    for i, pos in enumerate(positions):
        if i < len(binary_data):
            img.flat[pos] = (int(img.flat[pos]) & 0xFE) | int(binary_data[i])

    output_path = image_path.replace(".", f"_{username}_stego.")
    cv2.imwrite(output_path, img)

    # Encrypt positions before saving
    fernet = get_fernet()
    positions_json = json.dumps(positions)
    encrypted_positions = fernet.encrypt(positions_json.encode())
    
    positions_path = output_path + "_positions.enc"
    with open(positions_path, "wb") as f:
        f.write(encrypted_positions)

    save_auth_data(username, password)
    
    messagebox.showinfo("Success", f"User '{username}' registered! Use {output_path} as your password image.", parent=signup_window)

def extract_password_from_image(stego_image_path):
    positions_path = stego_image_path + "_positions.enc"

    try:
        # Decrypt positions file
        fernet = get_fernet()
        with open(positions_path, "rb") as f:
            encrypted_positions = f.read()
        
        positions_json = fernet.decrypt(encrypted_positions).decode()
        positions = json.loads(positions_json)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return None

    img = cv2.imread(stego_image_path)
    binary_data = "".join(str(img.flat[pos] & 1) for pos in positions)

    stop_marker = binary_data.find("1111111111111110")
    if stop_marker == -1:
        return None  

    extracted_binary = binary_data[:stop_marker]
    extracted_password = binary_to_text(extracted_binary)

    return extracted_password

def login():
    username = username_entry.get().strip()
    stego_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg")])

    if not username:
        messagebox.showerror("Error", "Please enter a username.", parent=login_window)
        return
    if not stego_image_path:
        return

    extracted_password = extract_password_from_image(stego_image_path)
    auth_data = load_auth_data()
    
    # No password found or user not found
    if not extracted_password or username not in auth_data:
        messagebox.showerror("Login Failed", "Invalid credentials.", parent=login_window)
        return

    # Verify password hash
    if verify_password(auth_data[username], extracted_password):
        messagebox.showinfo("Login Successful", "Welcome back!", parent=login_window)
    else:
        messagebox.showerror("Login Failed", "Invalid credentials.", parent=login_window)

def toggle_password_visibility():
    if show_password_var.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")

def open_signup_window():
    global signup_window, username_entry, password_entry, show_password_var

    signup_window, frame = create_styled_window("Signup - Image Authentication")
    
    create_styled_label(frame, "Signup", 18, True).pack(pady=(0, 20))
    
    create_styled_label(frame, "Username").pack(anchor="w", pady=(0, 5))
    username_entry = create_styled_entry(frame)
    username_entry.pack(fill="x", pady=(0, 15))

    create_styled_label(frame, "Password").pack(anchor="w", pady=(0, 5))
    password_entry = create_styled_entry(frame, show="*")
    password_entry.pack(fill="x", pady=(0, 5))

    show_password_var = tk.BooleanVar()
    show_password_checkbox = tk.Checkbutton(
        frame, 
        text="Show Password", 
        variable=show_password_var, 
        font=("Arial", 10),
        bg="white",
        command=toggle_password_visibility
    )
    show_password_checkbox.pack(anchor="w", pady=(0, 15))

    create_styled_button(frame, "Select Image & Register", signup, width=20).pack(pady=(15, 0))
    
    # Back link
    back_link = tk.Label(
        frame,
        text="Back to Main",
        font=("Arial", 10, "underline"),
        fg="#6060b0",
        cursor="hand2",
        bg="white"
    )
    back_link.pack(pady=(10, 0))
    back_link.bind("<Button-1>", lambda e: signup_window.destroy())

def open_login_window():
    global login_window, username_entry

    login_window, frame = create_styled_window("Login - Image Authentication", height=350)
    
    create_styled_label(frame, "Login", 18, True).pack(pady=(0, 20))
    
    create_styled_label(frame, "Username").pack(anchor="w", pady=(0, 5))
    username_entry = create_styled_entry(frame)
    username_entry.pack(fill="x", pady=(0, 20))

    remember_me_var = tk.BooleanVar()
    remember_me_checkbox = tk.Checkbutton(
        frame, 
        text="Remember Me", 
        variable=remember_me_var, 
        font=("Arial", 10),
        bg="white"
    )
    remember_me_checkbox.pack(anchor="w", pady=(0, 20))

    create_styled_button(frame, "Select Image & Login", login).pack(pady=(5, 15))
    
    # Back link
    back_link = tk.Label(
        frame,
        text="Back to Main",
        font=("Arial", 10, "underline"),
        fg="#6060b0",
        cursor="hand2",
        bg="white"
    )
    back_link.pack(pady=(10, 0))
    back_link.bind("<Button-1>", lambda e: login_window.destroy())

# Main Window
root = tk.Tk()
root.title("Image Authentication System")
root.configure(bg="white")
root.geometry("400x350")

# Center the window
root.update_idletasks()
x = (root.winfo_screenwidth() - 400) // 2
y = (root.winfo_screenheight() - 350) // 2
root.geometry(f"+{x}+{y}")

frame = tk.Frame(root, bg="white", padx=30, pady=30)
frame.pack(fill=tk.BOTH, expand=True)

create_styled_label(frame, "Image Authentication System", 16, True).pack(pady=(0, 25))

create_styled_button(frame, "Signup", open_signup_window).pack(pady=(0, 15))
create_styled_button(frame, "Login", open_login_window).pack(pady=(0, 15))

root.mainloop()