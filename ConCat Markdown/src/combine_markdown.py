import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

def _is_ignored_name(name):
    return name.startswith(".") or name.startswith("_")


def _build_header(file_path, root_folder):
    relative_path = file_path.relative_to(root_folder)
    friendly_name = file_path.stem.replace("_", " ")
    dir_name = str(relative_path.parent)

    if dir_name and dir_name != ".":
        return f"{dir_name} - {friendly_name}"
    return friendly_name


def _collect_markdown_files(folder_path):
    markdown_files = []

    for current_root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not _is_ignored_name(d)]

        for file_name in files:
            if file_name.lower().endswith(".md") and not _is_ignored_name(file_name):
                markdown_files.append(Path(current_root) / file_name)

    markdown_files.sort()
    return markdown_files


def unify_markdown_files(folder_path, output_file_path):
    source_folder = Path(folder_path)
    destination_file = Path(output_file_path)

    if not source_folder.exists():
        show_error("Invalid Folder", f"The folder '{source_folder}' does not exist.")
        return False

    if not source_folder.is_dir():
        show_error("Invalid Folder", f"'{source_folder}' is not a directory.")
        return False

    if not os.access(source_folder, os.R_OK):
        show_error("Permission Error", f"Cannot read from folder '{source_folder}'.")
        return False

    print(f"Scanning folder: {source_folder}")
    markdown_files = _collect_markdown_files(source_folder)

    if not markdown_files:
        show_error("No Files Found", "No Markdown files found in the selected folder.")
        return False

    print(f"Found {len(markdown_files)} markdown file(s). Processing...")

    processed_count = 0
    skipped_count = 0

    try:
        with destination_file.open("w", encoding="utf-8") as output_file:
            for index, file_path in enumerate(markdown_files, 1):
                relative_path = file_path.relative_to(source_folder)
                print(f"Processing {index}/{len(markdown_files)}: {relative_path}")

                try:
                    content = file_path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as exc:
                    print(f"  Error processing '{file_path}': {exc}")
                    skipped_count += 1
                    continue

                if not content.strip():
                    print(f"  Skipped (empty): {relative_path}")
                    skipped_count += 1
                    continue

                header = _build_header(file_path, source_folder)
                output_file.write(f"# {header}\n\n")
                output_file.write(content)

                if index < len(markdown_files):
                    output_file.write("\n\n<div style=\"page-break-after: always;\"></div>\n\n")

                processed_count += 1

    except OSError as exc:
        show_error("Write Error", f"Failed to write to '{destination_file}': {exc}")
        return False

    summary = f"Successfully processed {processed_count} file(s) into '{destination_file.name}'"
    if skipped_count > 0:
        summary += f"\n{skipped_count} file(s) were skipped due to errors or empty content."

    print(f"\n{summary}")
    show_info("Success", summary)
    return True

def show_error(title, message):
    """Display error message in GUI and console."""
    print(f"ERROR - {title}: {message}", file=sys.stderr)
    try:
        messagebox.showerror(title, message)
    except tk.TclError:
        pass

def show_info(title, message):
    """Display info message in GUI and console."""
    print(f"INFO - {title}: {message}")
    try:
        messagebox.showinfo(title, message)
    except tk.TclError:
        pass

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
        except tk.TclError:
            pass
    finally:
        # Properly destroy the tkinter root window
        if root:
            try:
                root.destroy()
            except tk.TclError:
                pass

if __name__ == "__main__":
    try:
        ask_user_for_folder_and_file()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)