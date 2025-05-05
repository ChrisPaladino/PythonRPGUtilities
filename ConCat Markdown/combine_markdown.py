import os
import tkinter as tk
from tkinter import filedialog

def unify_markdown_files(folder_path, output_file_path):
    markdown_files = []
    for root, dirs, files in os.walk(folder_path):
        # Filter out hidden or special directories (e.g., .obsidian, _trash)
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]  # Exclude hidden and underscored folders
        
        for file in files:
            if file.endswith('.md') and not file.startswith('.') and not file.startswith('_'):  # Exclude hidden and underscored .md files
                full_path = os.path.join(root, file)
                markdown_files.append(full_path)
    
    if not markdown_files:
        print("No Markdown files found in the selected folder.")
        return
    
    # Sort by full path to respect folder hierarchy (e.g., 1-Sessions before 2-PCs)
    markdown_files.sort()  # Default sort respects folder structure
    
    try:
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for i, file_path in enumerate(markdown_files, 1):
                try:
                    # Use only the filename (without path) for the header
                    file_name = os.path.basename(file_path)
                    friendly_name = os.path.splitext(file_name)[0].replace('_', ' ')
                    output_file.write(f"# {friendly_name}\n\n")
                    
                    with open(file_path, 'r', encoding='utf-8') as input_file:
                        content = input_file.read()
                        output_file.write(content)
                    
                    # Only add page break if not the last file
                    if i < len(markdown_files):
                        output_file.write('\n\n<div style="page-break-after: always;"></div>\n\n')
                except (IOError, UnicodeDecodeError) as e:
                    print(f"Error processing '{file_path}': {e}")
                    continue  # Skip problematic files without crashing
            
        print(f"All markdown files unified into '{output_file_path}' with page breaks.")
    except IOError as e:
        print(f"Failed to write to '{output_file_path}': {e}")

def ask_user_for_folder_and_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    folder_path = filedialog.askdirectory(title="Select Folder Containing Markdown Files")
    if not folder_path:
        print("Folder selection cancelled.")
        return
    
    output_file_path = filedialog.asksaveasfilename(
        defaultextension=".md",
        filetypes=[("Markdown files", "*.md")],
        title="Save the unified Markdown file as...",
        initialfile="unified_notes.md"  # Suggest a default name
    )
    if not output_file_path:
        print("File save cancelled.")
        return
    
    unify_markdown_files(folder_path, output_file_path)

if __name__ == "__main__":
    ask_user_for_folder_and_file()