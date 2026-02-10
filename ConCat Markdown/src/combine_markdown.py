import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

def unify_markdown_files(folder_path, output_file_path):
    # Validate input folder
    if not os.path.exists(folder_path):
        show_error("Invalid Folder", f"The folder '{folder_path}' does not exist.")
        return False
    
    if not os.path.isdir(folder_path):
        show_error("Invalid Folder", f"'{folder_path}' is not a directory.")
        return False
    
    if not os.access(folder_path, os.R_OK):
        show_error("Permission Error", f"Cannot read from folder '{folder_path}'.")
        return False
    
    print(f"Scanning folder: {folder_path}")
    markdown_files = []
    for root, dirs, files in os.walk(folder_path):
        # Filter out hidden or special directories (e.g., .obsidian, _trash)
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]  # Exclude hidden and underscored folders
        
        for file in files:
            if file.endswith('.md') and not file.startswith('.') and not file.startswith('_'):  # Exclude hidden and underscored .md files
                full_path = os.path.join(root, file)
                markdown_files.append(full_path)
    
    if not markdown_files:
        show_error("No Files Found", "No Markdown files found in the selected folder.")
        return False
    
    # Sort by full path to respect folder hierarchy (e.g., 1-Sessions before 2-PCs)
    markdown_files.sort()  # Default sort respects folder structure
    
    print(f"Found {len(markdown_files)} markdown file(s). Processing...")
    
    try:
        processed_count = 0
        skipped_count = 0
        
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for i, file_path in enumerate(markdown_files, 1):
                try:
                    # Create header with relative path for context
                    relative_path = os.path.relpath(file_path, folder_path)
                    file_name = os.path.basename(file_path)
                    friendly_name = os.path.splitext(file_name)[0].replace('_', ' ')
                    
                    # If file is in a subdirectory, include path info
                    dir_name = os.path.dirname(relative_path)
                    if dir_name and dir_name != '.':
                        header = f"{dir_name} - {friendly_name}"
                    else:
                        header = friendly_name
                    
                    print(f"Processing {i}/{len(markdown_files)}: {relative_path}")
                    
                    with open(file_path, 'r', encoding='utf-8') as input_file:
                        content = input_file.read()
                    
                    # Only write if content is not empty (after stripping whitespace)
                    if content.strip():
                        output_file.write(f"# {header}\n\n")
                        output_file.write(content)
                        
                        # Only add page break if not the last file
                        if i < len(markdown_files):
                            output_file.write('\n\n<div style="page-break-after: always;"></div>\n\n')
                        
                        processed_count += 1
                    else:
                        print(f"  Skipped (empty): {relative_path}")
                        skipped_count += 1
                        
                except (IOError, UnicodeDecodeError) as e:
                    print(f"  Error processing '{file_path}': {e}")
                    skipped_count += 1
                    continue  # Skip problematic files without crashing
        
        summary = f"Successfully processed {processed_count} file(s) into '{os.path.basename(output_file_path)}'"
        if skipped_count > 0:
            summary += f"\n{skipped_count} file(s) were skipped due to errors or empty content."
        
        print(f"\n{summary}")
        show_info("Success", summary)
        return True
        
    except IOError as e:
        error_msg = f"Failed to write to '{output_file_path}': {e}"
        show_error("Write Error", error_msg)
        return False

def show_error(title, message):
    """Display error message in GUI and console."""
    print(f"ERROR - {title}: {message}", file=sys.stderr)
    try:
        messagebox.showerror(title, message)
    except:
        pass  # Fallback if messagebox fails

def show_info(title, message):
    """Display info message in GUI and console."""
    print(f"INFO - {title}: {message}")
    try:
        messagebox.showinfo(title, message)
    except:
        pass  # Fallback if messagebox fails

def ask_user_for_folder_and_file():
    root = None
    try:
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
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(error_msg, file=sys.stderr)
        try:
            messagebox.showerror("Error", error_msg)
        except:
            pass
    finally:
        # Properly destroy the tkinter root window
        if root:
            try:
                root.destroy()
            except:
                pass

if __name__ == "__main__":
    try:
        ask_user_for_folder_and_file()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)