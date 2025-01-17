import tkinter as tk
from tkinter import ttk
import json
import os

# Set up relative paths
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
JSON_PATH = os.path.join(script_dir, "data", "trademarks.json")

def load_trademarks():
    try:
        with open(JSON_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"trademarks": []}

trademarks_data = load_trademarks()

# Main Application
class TrademarkManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trademark Manager")
        self.create_ui()

    def create_ui(self):
        # Main layout
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Paned window for resizing
        paned_window = ttk.PanedWindow(main_frame, orient="vertical")
        paned_window.pack(fill="both", expand=True)

        # Top frame for search and listbox
        search_list_frame = ttk.Frame(paned_window)
        paned_window.add(search_list_frame, weight=1)

        search_frame = ttk.Frame(search_list_frame)
        search_frame.pack(fill="x", pady=5)

        search_label = ttk.Label(search_frame, text="Search Trademarks:")
        search_label.pack(side="left", padx=5)

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(fill="x", expand=True, side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_trademarks)

        self.trademark_listbox = tk.Listbox(search_list_frame, height=10)
        self.trademark_listbox.pack(fill="both", expand=True, pady=5)
        self.trademark_listbox.bind("<<ListboxSelect>>", self.view_trademark_details)

        # Bottom frame for details
        details_frame = ttk.Frame(paned_window)
        paned_window.add(details_frame, weight=3)

        self.trademark_details = tk.Text(details_frame, wrap="word", state="disabled")
        self.trademark_details.pack(fill="both", expand=True, padx=5, pady=5)

        # Populate Listbox with initial data
        self.populate_trademark_list()

        # Enable resizing behavior
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def populate_trademark_list(self):
        self.trademark_listbox.delete(0, tk.END)
        sorted_trademarks = sorted(
            trademarks_data["trademarks"],
            key=lambda t: (t["source"], t["type"], t["name"])
        )
        for trademark in sorted_trademarks:
            display_text = f"{trademark['source']}: {trademark['type']}: {trademark['name']}"
            self.trademark_listbox.insert(tk.END, display_text)

    def filter_trademarks(self, event):
        query = self.search_entry.get().lower()
        self.trademark_listbox.delete(0, tk.END)
        sorted_trademarks = sorted(
            trademarks_data["trademarks"],
            key=lambda t: (t["source"], t["type"], t["name"])
        )
        for trademark in sorted_trademarks:
            display_text = f"{trademark['source']}: {trademark['type']}: {trademark['name']}"
            if query in display_text.lower() or any(
                query in field.lower() for field in [
                    trademark.get("description", ""),
                    " ".join(trademark.get("traits", [])),
                    " ".join(trademark.get("flaws", [])),
                    " ".join(trademark.get("gear", [])),
                    " ".join(adv.get("name", "") + " " + adv.get("description", "") for adv in trademark.get("advantages", []))
                ]
            ):
                self.trademark_listbox.insert(tk.END, display_text)

    def view_trademark_details(self, event):
        selected = self.trademark_listbox.curselection()
        if selected:
            selected_text = self.trademark_listbox.get(selected)
            source, type_, name = map(str.strip, selected_text.split(":", 2))
            for trademark in trademarks_data["trademarks"]:
                if (
                    trademark["source"] == source
                    and trademark["type"] == type_
                    and trademark["name"] == name
                ):
                    self.display_trademark(trademark)
                    break

    def display_trademark(self, trademark):
        details = f"Name: {trademark['name']}\n"
        details += f"Source: {trademark['source']}\n"
        details += f"Type: {trademark['type']}\n"
        details += f"Description: {trademark['description']}\n\n"
        details += "Traits:\n" + "\n".join(f"- {trait}" for trait in trademark.get("traits", [])) + "\n\n"
        details += "Flaws:\n" + "\n".join(f"- {flaw}" for flaw in trademark.get("flaws", [])) + "\n\n"
        details += "Gear:\n" + "\n".join(f"- {gear}" for gear in trademark.get("gear", [])) + "\n\n"
        details += "Advantages:\n" + "\n".join(
            f"- {adv['name']}: {adv['description']}" for adv in trademark.get("advantages", [])
        )

        self.trademark_details.config(state="normal")
        self.trademark_details.delete("1.0", tk.END)
        self.trademark_details.insert("1.0", details)
        self.trademark_details.config(state="disabled")

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = TrademarkManagerApp(root)
    root.geometry("800x600")
    root.mainloop()
