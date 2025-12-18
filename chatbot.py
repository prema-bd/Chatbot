import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import speech_recognition as sr
from knowledge import education_data
import threading
import time

# ------------------- Conversation State -------------------
conversation_state = {}

# ------------------- Theme -------------------
theme = {
    "bg": "#1a001a",
    "chat_bg": "#2a002a",
    "fg": "#ffffff",
    "user_bg": "#ff00ff",
    "bot_bg": "#330033",
    "accent": "#ff00ff"
}

# ------------------- Main Window -------------------
root = tk.Tk()
root.title("EduBot 📚")
root.geometry("500x650")
root.configure(bg=theme["bg"])

# ------------------- Top Bar -------------------
top_bar = tk.Frame(root, bg=theme["bg"])
top_bar.pack(fill=tk.X, pady=5)

def toggle_theme():
    global theme, theme_btn
    if theme["bg"] == "#1a001a":  # Dark -> Light
        theme = {
            "bg": "#ffffff",
            "chat_bg": "#f0f0f0",
            "fg": "#000000",
            "user_bg": "#ff00ff",
            "bot_bg": "#e0e0e0",
            "accent": "#ff00ff"
        }
        theme_btn.config(text="🌙")  # moon icon
    else:  # Light -> Dark
        theme = {
            "bg": "#1a001a",
            "chat_bg": "#2a002a",
            "fg": "#ffffff",
            "user_bg": "#ff00ff",
            "bot_bg": "#330033",
            "accent": "#ff00ff"
        }
        theme_btn.config(text="🌞")  # sun icon

    # Apply theme to all widgets
    root.configure(bg=theme["bg"])
    top_bar.configure(bg=theme["bg"])
    title.configure(bg=theme["bg"], fg=theme["accent"])
    input_frame.configure(bg=theme["bg"])
    user_entry.configure(bg=theme["chat_bg"], fg=theme["fg"], insertbackground=theme["fg"])
    canvas.configure(bg=theme["chat_bg"])
    scrollable_frame.configure(bg=theme["chat_bg"])

theme_btn = tk.Button(top_bar, text="🌞", command=toggle_theme,
                      bg=theme["bg"], fg=theme["accent"], bd=0, font=("Arial", 12, "bold"))
theme_btn.pack(side=tk.RIGHT, padx=10)

title = tk.Label(top_bar, text="EduBot 📚", bg=theme["bg"], fg=theme["accent"],
                 font=("Arial", 16, "bold"))
title.pack(side=tk.LEFT, padx=10)

# ------------------- Chat Display -------------------
chat_frame = tk.Frame(root)
chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)

canvas = tk.Canvas(chat_frame, bg=theme["chat_bg"], bd=0, highlightthickness=0)
scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg=theme["chat_bg"])

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# ------------------- Input Row -------------------
input_frame = tk.Frame(root, bg=theme["bg"])
input_frame.pack(fill=tk.X, pady=5)

# + Symbol dropdown
def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        add_message(f"You uploaded {file_path}", "bot")

def take_photo():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        add_message("Could not open camera.", "bot")
        return
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Captured Photo", frame)
        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files","*.png"),("JPEG files","*.jpg")])
        if save_path:
            cv2.imwrite(save_path, frame)
            add_message(f"Photo saved at {save_path}", "bot")
    cap.release()
    cv2.destroyAllWindows()

plus_btn = tk.Menubutton(input_frame, text="+", bg=theme["accent"], fg="#fff",
                         font=("Arial", 14, "bold"), relief=tk.FLAT)
menu = tk.Menu(plus_btn, tearoff=0, bg=theme["chat_bg"], fg=theme["fg"])
plus_btn.config(menu=menu)
menu.add_command(label="Upload File", command=upload_file)
menu.add_command(label="Camera", command=take_photo)
plus_btn.pack(side=tk.LEFT, padx=5)

# Entry box
user_entry = tk.Entry(input_frame, font=("Arial", 12), bg=theme["chat_bg"], fg=theme["fg"],
                      insertbackground=theme["fg"])
user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

# Send button
def send_message():
    msg = user_entry.get().strip()
    if not msg:
        return
    user_entry.delete(0, tk.END)
    add_message(msg, "user")
    reply = get_reply(msg)
    add_message(reply, "bot", animate=True)

send_btn = tk.Button(input_frame, text="➡", bg=theme["accent"], fg="#fff", width=4,
                     command=send_message)
send_btn.pack(side=tk.LEFT, padx=5)

# Voice button
def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        add_message("Listening...", "bot")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        add_message(text, "user")
        reply = get_reply(text)
        add_message(reply, "bot", animate=True)
    except sr.UnknownValueError:
        add_message("Could not understand audio.", "bot")

voice_btn = tk.Button(input_frame, text="🎤", bg=theme["accent"], fg="#fff", width=4,
                      command=voice_input)
voice_btn.pack(side=tk.LEFT, padx=5)

# ------------------- Functions -------------------
def get_reply(user_msg):
    data = education_data["en"]
    msg = user_msg.lower().strip()

    # Check greetings
    if msg in data.get("greetings", []):
        conversation_state["stage"] = "greeted"
        return data.get("greetings_reply", "Hello!")

    # Check all other keys in the data
    for key in data:
        if key in ["greetings", "greetings_reply"]:
            continue
        if key in msg:
            return data[key]

    return "Sorry, I can't answer that right now."

def add_message(msg, sender="user", animate=False):
    bubble_bg = theme["user_bg"] if sender=="user" else theme["bot_bg"]
    fg_color = "#ffffff" if sender=="user" else theme["fg"]
    anchor = "e" if sender=="user" else "w"

    msg_label = tk.Label(scrollable_frame, text="", bg=bubble_bg, fg=fg_color,
                         font=("Arial", 11), wraplength=300, justify="left", padx=10, pady=5)
    msg_label.pack(anchor=anchor, pady=5, padx=10)

    if animate and sender=="bot":
        def animate_text():
            for char in msg:
                msg_label.config(text=msg_label.cget("text")+char)
                canvas.update()
                time.sleep(0.02)
        threading.Thread(target=animate_text).start()
    else:
        msg_label.config(text=msg)
    canvas.update_idletasks()
    canvas.yview_moveto(1)

# ------------------- Run App -------------------
root.mainloop()
