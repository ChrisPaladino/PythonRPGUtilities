import os
import tkinter as tk
from tkinter import filedialog

def unify_markdown_files(folder_path, output_file_path):
    markdown_files = []
    for root, dirs, files in os.walk(folder_path):
        # Filter out directories that start with '.' or '_'
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
        
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                markdown_files.append(full_path)
    
    markdown_files.sort()
    
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for file_path in markdown_files:
            # Extract the file name from the path
            file_name = os.path.basename(file_path)
            # Remove the '.md' extension and replace underscores with spaces for the header
            friendly_name = os.path.splitext(file_name)[0].replace('_', ' ')
            # Write the header
            output_file.write(f"# {friendly_name}\n\n")
            
            with open(file_path, 'r', encoding='utf-8') as input_file:
                content = input_file.read()
                output_file.write(content)
                # Add a page break after the content
                output_file.write('\n<div style="page-break-after: always;"></div>\n\n')
    
    print(f"All markdown files have been unified into '{output_file_path}', with page breaks included.")

def ask_user_for_folder_and_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    folder_path = filedialog.askdirectory(title="Select Folder Containing Markdown Files")
    if not folder_path:
        print("Folder selection cancelled.")
        return
    
    output_file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md")], title="Save the unified Markdown file as...")
    if not output_file_path:
        print("File save cancelled.")
        return
    
    unify_markdown_files(folder_path, output_file_path)
    print("Operation completed successfully.")

ask_user_for_folder_and_file()
