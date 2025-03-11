import tkinter as tk
from tkinter import ttk
import pyttsx3
import re
import threading

# Initialize the TTS engine
engine = pyttsx3.init()
is_speaking = False
stop_event = threading.Event()

def clean_text(text):
    """Remove markup symbols but keep the enclosed text."""
    cleaned = text
    cleaned = re.sub(r'#+\s*', '', cleaned)
    cleaned = re.sub(r'\[\[(.*?)\]\]', r'\1', cleaned)
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
    cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
    cleaned = re.sub(r'__(.*?)__', r'\1', cleaned)
    cleaned = re.sub(r'~~(.*?)~~', r'\1', cleaned)
    return cleaned.strip()

def update_text_box(*args):
    """Clean text and update the Text widget."""
    original_text = text_box.get("1.0", tk.END).strip()
    cleaned_text = clean_text(original_text)
    if original_text != cleaned_text:
        text_box.delete("1.0", tk.END)
        text_box.insert("1.0", cleaned_text)
    count_paragraphs()

def count_paragraphs(*args):
    text_content = text_box.get("1.0", tk.END).strip()
    if text_content:
        lines = [line for line in text_content.split("\n") if line.strip()]
        result_label.config(text=f"Number of paragraphs (split by newlines): {len(lines)}")
    else:
        result_label.config(text="Number of paragraphs (split by newlines): 0")

def speak_text_thread():
    """Run TTS in a thread with play/stop."""
    global is_speaking
    text_content = text_box.get("1.0", tk.END).strip()
    if not text_content or is_speaking:
        return
    
    is_speaking = True
    stop_event.clear()
    
    # Set properties before speaking
    engine.setProperty('rate', speed_scale.get())
    engine.setProperty('volume', volume_scale.get())
    engine.setProperty('voice', voices[voice_menu.current()].id)
    
    engine.say(text_content)
    engine.runAndWait()  # Blocking call, but in a thread
    
    if stop_event.is_set():
        engine.stop()  # Ensure queue is cleared
    is_speaking = False

def speak_text():
    """Start speaking."""
    global is_speaking
    if not is_speaking:
        threading.Thread(target=speak_text_thread, daemon=True).start()

def stop_speaking():
    """Stop the TTS."""
    global is_speaking
    if is_speaking:
        stop_event.set()
        engine.stop()  # Stop current speech and clear queue
        is_speaking = False

# Create the main window
root = tk.Tk()
root.title("Paragraph Counter with pyttsx3")

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=0)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

text_box = tk.Text(root, wrap="word")
text_box.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

text_box.bind("<KeyRelease>", update_text_box)
text_box.bind("<<Paste>>", lambda event: root.after(100, update_text_box))

result_label = ttk.Label(root, text="Number of paragraphs (split by newlines): 0")
result_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")

controls_frame = ttk.Frame(root)
controls_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

ttk.Label(controls_frame, text="Speed (wpm):").pack(side=tk.LEFT, padx=5)
speed_scale = tk.Scale(controls_frame, from_=50, to=300, orient=tk.HORIZONTAL)
speed_scale.set(175)
speed_scale.pack(side=tk.LEFT, padx=5)

ttk.Label(controls_frame, text="Volume:").pack(side=tk.LEFT, padx=5)
volume_scale = tk.Scale(controls_frame, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL)
volume_scale.set(1.0)
volume_scale.pack(side=tk.LEFT, padx=5)

ttk.Label(controls_frame, text="Voice:").pack(side=tk.LEFT, padx=5)
voices = engine.getProperty('voices')
voice_names = [voice.name for voice in voices]
voice_menu = ttk.Combobox(controls_frame, values=voice_names, state="readonly")
voice_menu.current(0)
voice_menu.pack(side=tk.LEFT, padx=5)

speak_button = ttk.Button(controls_frame, text="Speak", command=speak_text)
speak_button.pack(side=tk.LEFT, padx=5)

stop_button = ttk.Button(controls_frame, text="Stop", command=stop_speaking)
stop_button.pack(side=tk.LEFT, padx=5)

count_paragraphs()
root.mainloop()