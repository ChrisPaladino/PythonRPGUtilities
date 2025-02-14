import tkinter as tk
from tkinter import ttk

def count_paragraphs():
    # Get all the text from the Text widget (from index "1.0" up to "end") and strip whitespace
    text_content = text_box.get("1.0", tk.END).strip()
    
    if text_content:
        # Split on every newline, remove empty lines after stripping
        lines = [line for line in text_content.split("\n") if line.strip()]
        result_label.config(text=f"Number of paragraphs (split by newlines): {len(lines)}")
    else:
        result_label.config(text="Number of paragraphs (split by newlines): 0")

# Create the main window
root = tk.Tk()
root.title("Paragraph Counter")

# Make the rows and columns expandable
root.rowconfigure(0, weight=1)        # The row with the Text widget
root.rowconfigure(1, weight=0)        # The row with the button/label
root.columnconfigure(0, weight=1)     # First column
root.columnconfigure(1, weight=1)     # Second column, so label can resize if needed

# Create a large Text widget and let it expand
text_box = tk.Text(root, wrap="word")  # wrap="word" for neat wrapping
text_box.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Create a button to trigger the paragraph count
count_button = ttk.Button(root, text="Count Paragraphs", command=count_paragraphs)
count_button.grid(row=1, column=0, padx=10, pady=10, sticky="e")

# Create a label to show results, also let it expand horizontally if needed
result_label = ttk.Label(root, text="Number of paragraphs: 0")
result_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")

# Start the Tkinter event loop
root.mainloop()
