import tkinter as tk
from tkinter import ttk
import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()

def count_paragraphs(*args):
    # Get all the text from the Text widget and strip whitespace
    text_content = text_box.get("1.0", tk.END).strip()
    
    if text_content:
        # Split on every newline, remove empty lines after stripping
        lines = [line for line in text_content.split("\n") if line.strip()]
        result_label.config(text=f"Number of paragraphs (split by newlines): {len(lines)}")
    else:
        result_label.config(text="Number of paragraphs (split by newlines): 0")

def speak_text():
    # Get the text to speak
    text_content = text_box.get("1.0", tk.END).strip()
    if not text_content:
        return  # No text to speak
    
    # Set TTS properties from controls
    engine.setProperty('rate', speed_scale.get())    # Speed in words per minute
    engine.setProperty('volume', volume_scale.get()) # Volume (0.0 to 1.0)
    engine.setProperty('voice', voices[voice_menu.current()].id)  # Selected voice
    
    # Speak the text
    engine.say(text_content)
    engine.runAndWait()

# Create the main window
root = tk.Tk()
root.title("Paragraph Counter with Text-to-Speech")

# Make the rows and columns expandable
root.rowconfigure(0, weight=1)  # Text widget row
root.rowconfigure(1, weight=0)  # Label row
root.rowconfigure(2, weight=0)  # Controls row
root.columnconfigure(0, weight=1)  # First column
root.columnconfigure(1, weight=1)  # Second column

# Create a large Text widget and let it expand
text_box = tk.Text(root, wrap="word")
text_box.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Bind the KeyRelease event to update paragraph count in real-time
text_box.bind("<KeyRelease>", count_paragraphs)

# Create a label to show results
result_label = ttk.Label(root, text="Number of paragraphs (split by newlines): 0")
result_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")

# TTS Controls Frame
controls_frame = ttk.Frame(root)
controls_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

# Speed control
ttk.Label(controls_frame, text="Speed (wpm):").pack(side=tk.LEFT, padx=5)
speed_scale = tk.Scale(controls_frame, from_=50, to=300, orient=tk.HORIZONTAL)
speed_scale.set(175)  # Default speed
speed_scale.pack(side=tk.LEFT, padx=5)

# Volume control
ttk.Label(controls_frame, text="Volume:").pack(side=tk.LEFT, padx=5)
volume_scale = tk.Scale(controls_frame, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL)
volume_scale.set(1.0)  # Default volume
volume_scale.pack(side=tk.LEFT, padx=5)

# Voice selection
ttk.Label(controls_frame, text="Voice:").pack(side=tk.LEFT, padx=5)
voices = engine.getProperty('voices')  # Get available voices
voice_names = [voice.name for voice in voices]
voice_menu = ttk.Combobox(controls_frame, values=voice_names, state="readonly")
voice_menu.current(0)  # Default to first voice
voice_menu.pack(side=tk.LEFT, padx=5)

# Speak button
speak_button = ttk.Button(controls_frame, text="Speak", command=speak_text)
speak_button.pack(side=tk.LEFT, padx=5)

# Initial call to set the count at startup
count_paragraphs()

# Start the Tkinter event loop
root.mainloop()