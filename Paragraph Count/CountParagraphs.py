import tkinter as tk
from tkinter import ttk
import pyttsx3
import re
import threading
import time

# Initialize the TTS engine
engine = pyttsx3.init()
is_speaking = False
stop_event = threading.Event()
pause_event = threading.Event()
current_position = 0  # Tracks character position in text

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

def split_into_sentences(text):
    """Split text into sentences for finer control."""
    # Simple sentence splitting (improve with regex or NLP if needed)
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

def speak_text_thread():
    """Run TTS in a thread with real-time updates and pause/resume."""
    global is_speaking, current_position
    text_content = text_box.get("1.0", tk.END).strip()
    if not text_content or is_speaking:
        return
    
    is_speaking = True
    stop_event.clear()
    pause_event.clear()
    
    sentences = split_into_sentences(text_content)
    total_text = " ".join(sentences)  # Reconstruct full text for position tracking
    
    if current_position > 0:
        # Resume from paused position
        remaining_text = total_text[current_position:]
        sentences = split_into_sentences(remaining_text)
    else:
        remaining_text = total_text
    
    for sentence in sentences:
        if stop_event.is_set():
            break
        if pause_event.is_set():
            current_position = total_text.index(sentence, current_position if current_position > 0 else 0)
            break
        
        # Apply properties before speaking each sentence
        engine.setProperty('rate', speed_scale.get())
        engine.setProperty('volume', volume_scale.get())
        engine.setProperty('voice', voices[voice_menu.current()].id)
        
        engine.say(sentence)
        engine.startLoop(False)
        while engine.isBusy() and not stop_event.is_set() and not pause_event.is_set():
            engine.iterate()
            root.update()
            time.sleep(0.05)  # 50ms delay for responsiveness
        engine.endLoop()
        
        if not pause_event.is_set() and not stop_event.is_set():
            current_position += len(sentence) + 1  # +1 for space
    
    if stop_event.is_set() or not pause_event.is_set():
        current_position = 0  # Reset on stop or full completion
    is_speaking = False

def speak_text():
    """Start or resume speaking."""
    global is_speaking
    if not is_speaking:
        threading.Thread(target=speak_text_thread, daemon=True).start()
    elif pause_event.is_set():
        pause_event.clear()  # Resume from paused state
        threading.Thread(target=speak_text_thread, daemon=True).start()

def stop_speaking():
    """Stop the TTS and reset position."""
    global is_speaking, current_position
    if is_speaking:
        stop_event.set()
        engine.stop()
        is_speaking = False
        current_position = 0
        pause_event.clear()

def pause_speaking():
    """Pause the TTS at current position."""
    global is_speaking
    if is_speaking and not pause_event.is_set():
        pause_event.set()

# Create the main window
root = tk.Tk()
root.title("Paragraph Counter with Text-to-Speech")

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

pause_button = ttk.Button(controls_frame, text="Pause", command=pause_speaking)
pause_button.pack(side=tk.LEFT, padx=5)

count_paragraphs()
root.mainloop()