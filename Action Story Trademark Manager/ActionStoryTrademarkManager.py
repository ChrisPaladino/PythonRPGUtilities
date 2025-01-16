import tkinter as tk
from tkinter import ttk, messagebox
import json

# Load JSON Data
JSON_PATH = "data/trademarks.json"
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

        # Search Bar
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill="x", pady=5)

        search_label = ttk.Label(search_frame, text="Search Trademarks:")
        search_label.pack(side="left", padx=5)

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(fill="x", expand=True, side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_trademarks)

        # Listbox for displaying search results
        self.trademark_listbox = tk.Listbox(main_frame, height=15)
        self.trademark_listbox.pack(fill="both", expand=True, pady=5)
        self.trademark_listbox.bind("<Double-1>", self.view_trademark_details)

        # Detailed Trademark Display
        details_frame = ttk.LabelFrame(main_frame, text="Trademark Details")
        details_frame.pack(fill="both", expand=True, pady=5)

        self.trademark_details = tk.Text(details_frame, wrap="word", state="disabled", height=10)
        self.trademark_details.pack(fill="both", expand=True, padx=5, pady=5)

        # Export Button
        export_button = ttk.Button(main_frame, text="Export Trademark", command=self.export_trademark)
        export_button.pack(pady=5)

        # Populate Listbox with initial data
        self.populate_trademark_list()

    def populate_trademark_list(self):
        self.trademark_listbox.delete(0, tk.END)
        for trademark in trademarks_data["trademarks"]:
            self.trademark_listbox.insert(tk.END, trademark["name"])

    def filter_trademarks(self, event):
        query = self.search_entry.get().lower()
        self.trademark_listbox.delete(0, tk.END)
        for trademark in trademarks_data["trademarks"]:
            if query in trademark["name"].lower() or any(query in field.lower() for field in [
                " ".join(trademark.get("traits", [])),
                " ".join(trademark.get("flaws", [])),
                " ".join(trademark.get("gear", []))
            ]):
                self.trademark_listbox.insert(tk.END, trademark["name"])

    def view_trademark_details(self, event):
        selected = self.trademark_listbox.curselection()
        if selected:
            trademark_name = self.trademark_listbox.get(selected)
            for trademark in trademarks_data["trademarks"]:
                if trademark["name"] == trademark_name:
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

    def export_trademark(self):
        text = self.trademark_details.get("1.0", tk.END).strip()
        if text:
            with open("trademark_export.txt", "w") as file:
                file.write(text)
            messagebox.showinfo("Export", "Trademark exported to trademark_export.txt")

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = TrademarkManagerApp(root)
    root.geometry("800x600")
    root.mainloop()
