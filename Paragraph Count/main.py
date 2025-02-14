import tkinter as tk
from tkinter import ttk

def count_paragraphs():
    # Get all the text from the Text widget (from index '1.0' up to 'end')
    text_content = text_box.get("1.0", tk.END).strip()
    
    if text_content:
        # Split text by blank lines (\n\n). Also strip each paragraph and remove empty ones.
        paragraphs = [p for p in text_content.split("\n") if p.strip()]
        result_label.config(text=f"Number of paragraphs: {len(paragraphs)}")
    else:
        result_label.config(text="Number of paragraphs: 0")

# Create the main window
root = tk.Tk()
root.title("Paragraph Counter")

# Create a large text box
text_box = tk.Text(root, width=80, height=20)
text_box.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# Create a button to trigger the count
count_button = ttk.Button(root, text="Count Paragraphs", command=count_paragraphs)
count_button.grid(row=1, column=0, padx=10, pady=10, sticky="e")

# Create a label to display the result
result_label = ttk.Label(root, text="Number of paragraphs: 0", anchor="w")
result_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")

# Start the Tkinter event loop
root.mainloop()
