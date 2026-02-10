import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import unicodedata
import sys

# Set up relative paths
script_dir = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(script_dir, "..", "data", "trademarks.json")

# Main Application
class TrademarkManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trademark Manager")
        self.root.geometry("800x600")
        
        # Data structures
        self.trademarks_data = {"trademarks": []}
        self.current_trademarks = []
        self.sorted_trademarks_cache = []
        
        # Load data
        self.load_trademarks()
        
        # Create UI
        self.create_ui()
        
    def normalize_text(self, text):
        """Normalize Unicode characters to ASCII-compatible forms."""
        if text is None:
            return ""
        return unicodedata.normalize("NFKC", str(text))
    
    def validate_trademark(self, trademark):
        """Validate and normalize a trademark entry."""
        if not isinstance(trademark, dict):
            return False
            
        # Ensure required fields exist with proper types
        trademark.setdefault("name", "Unknown")
        trademark.setdefault("source", "Unknown")
        trademark.setdefault("type", "Unknown")
        trademark.setdefault("description", "")
        
        # Ensure list fields are actually lists
        for field in ["traits", "flaws", "gear"]:
            if not isinstance(trademark.get(field), list):
                trademark[field] = []
                
        # Validate advantages structure
        if not isinstance(trademark.get("advantages"), list):
            trademark["advantages"] = []
        else:
            for adv in trademark["advantages"]:
                if isinstance(adv, dict):
                    adv.setdefault("name", "")
                    adv.setdefault("description", "")
        
        # Normalize all text fields once during load
        trademark["name"] = self.normalize_text(trademark["name"])
        trademark["source"] = self.normalize_text(trademark["source"])
        trademark["type"] = self.normalize_text(trademark["type"])
        trademark["description"] = self.normalize_text(trademark["description"])
        trademark["traits"] = [self.normalize_text(t) for t in trademark["traits"]]
        trademark["flaws"] = [self.normalize_text(f) for f in trademark["flaws"]]
        trademark["gear"] = [self.normalize_text(g) for g in trademark["gear"]]
        
        for adv in trademark["advantages"]:
            adv["name"] = self.normalize_text(adv.get("name", ""))
            adv["description"] = self.normalize_text(adv.get("description", ""))
            
        return True
    
    def load_trademarks(self):
        """Load and validate trademarks from JSON file."""
        try:
            if not os.path.exists(JSON_PATH):
                self.show_error("File Not Found", f"Could not find {JSON_PATH}")
                return
                
            with open(JSON_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
                
            if not isinstance(data, dict):
                self.show_error("Invalid Data", "JSON file must contain an object")
                return
                
            if "trademarks" not in data:
                self.show_error("Invalid Data", "JSON file must contain a 'trademarks' array")
                return
                
            if not isinstance(data["trademarks"], list):
                self.show_error("Invalid Data", "'trademarks' must be an array")
                return
            
            # Validate and normalize each trademark
            valid_trademarks = []
            for i, tm in enumerate(data["trademarks"]):
                if self.validate_trademark(tm):
                    valid_trademarks.append(tm)
                else:
                    print(f"Warning: Skipping invalid trademark at index {i}", file=sys.stderr)
            
            data["trademarks"] = valid_trademarks
            self.trademarks_data = data
            
            # Pre-sort and cache the data
            self.sorted_trademarks_cache = sorted(
                self.trademarks_data["trademarks"],
                key=lambda t: (t["source"], t["type"], t["name"])
            )
            
        except json.JSONDecodeError as e:
            self.show_error("JSON Error", f"Invalid JSON format: {str(e)}")
        except Exception as e:
            self.show_error("Error", f"Failed to load trademarks: {str(e)}")
    
    def show_error(self, title, message):
        """Show error message. Safe to call before UI is initialized."""
        try:
            if self.root.winfo_exists():
                messagebox.showerror(title, message)
            else:
                print(f"ERROR - {title}: {message}", file=sys.stderr)
        except:
            print(f"ERROR - {title}: {message}", file=sys.stderr)
    
    def refresh_data(self):
        """Reload data from JSON file."""
        self.load_trademarks()
        self.populate_trademark_list()
        messagebox.showinfo("Refresh", "Data reloaded successfully!")

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
        
        # Refresh button
        refresh_button = ttk.Button(search_frame, text="Refresh", command=self.refresh_data)
        refresh_button.pack(side="left", padx=5)

        # Listbox with scrollbar
        listbox_frame = ttk.Frame(search_list_frame)
        listbox_frame.pack(fill="both", expand=True, pady=5)

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
        self.trademark_listbox = tk.Listbox(
            listbox_frame, yscrollcommand=scrollbar.set, height=10
        )
        scrollbar.config(command=self.trademark_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.trademark_listbox.pack(fill="both", expand=True)
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
        
        # Keyboard shortcuts
        self.root.bind("<F5>", lambda e: self.refresh_data())
        self.root.bind("<Control-f>", lambda e: self.search_entry.focus())
    
    def populate_trademark_list(self):
        """Populate listbox with trademarks using cached sorted data."""
        self.trademark_listbox.delete(0, tk.END)
        self.current_trademarks = self.sorted_trademarks_cache.copy()
        
        for trademark in self.current_trademarks:
            display_text = f"{trademark['source']}: {trademark['type']}: {trademark['name']}"
            self.trademark_listbox.insert(tk.END, display_text)
            
        if not self.current_trademarks:
            self.display_trademark({"name": "No Data", "description": "No trademarks available."})

    def filter_trademarks(self, event):
        """Filter trademarks based on search query."""
        query = self.search_entry.get().lower()
        self.trademark_listbox.delete(0, tk.END)
        
        if not query:
            # No search query - show all trademarks from cache
            self.current_trademarks = self.sorted_trademarks_cache.copy()
            for trademark in self.current_trademarks:
                display_text = f"{trademark['source']}: {trademark['type']}: {trademark['name']}"
                self.trademark_listbox.insert(tk.END, display_text)
            return
        
        # Filter using cached sorted data
        matches = []
        for trademark in self.sorted_trademarks_cache:
            # Build searchable text (already normalized during load)
            searchable_parts = [
                trademark.get("source", ""),
                trademark.get("type", ""),
                trademark.get("name", ""),
                trademark.get("description", ""),
                " ".join(trademark.get("traits", [])),
                " ".join(trademark.get("flaws", [])),
                " ".join(trademark.get("gear", [])),
                " ".join(adv.get("name", "") + " " + adv.get("description", "") 
                        for adv in trademark.get("advantages", []))
            ]
            searchable_text = " ".join(searchable_parts).lower()
            
            if query in searchable_text:
                matches.append(trademark)
                display_text = f"{trademark['source']}: {trademark['type']}: {trademark['name']}"
                self.trademark_listbox.insert(tk.END, display_text)
                
        self.current_trademarks = matches
        if not matches:
            self.display_trademark({"name": "No Results", "description": "No trademarks match the search criteria."})

    def view_trademark_details(self, event):
        selected = self.trademark_listbox.curselection()
        if selected:
            index = selected[0]
            if index < len(self.current_trademarks):
                self.display_trademark(self.current_trademarks[index])
            else:
                self.display_trademark({"name": "Not Found", "description": "No matching trademark found."})

    def display_trademark(self, trademark):
        """Display trademark details (text already normalized during load)."""
        details = f"Name: {trademark.get('name', '')}\n"
        details += f"Source: {trademark.get('source', '')}\n"
        details += f"Type: {trademark.get('type', '')}\n"
        details += f"Description: {trademark.get('description', '')}\n\n"
        details += "Traits:\n" + "\n".join(f"- {trait}" for trait in trademark.get("traits", [])) + "\n\n"
        details += "Flaws:\n" + "\n".join(f"- {flaw}" for flaw in trademark.get("flaws", [])) + "\n\n"
        details += "Gear:\n" + "\n".join(f"- {gear}" for gear in trademark.get("gear", [])) + "\n\n"
        details += "Advantages:\n" + "\n".join(
            f"- {adv.get('name', '')}: {adv.get('description', '')}" 
            for adv in trademark.get("advantages", [])
        )

        self.trademark_details.config(state="normal")
        self.trademark_details.delete("1.0", tk.END)
        self.trademark_details.insert("1.0", details)
        self.trademark_details.config(state="disabled")

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = TrademarkManagerApp(root)
    root.mainloop()
