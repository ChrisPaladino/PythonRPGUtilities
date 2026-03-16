import tkinter as tk
from ui import RPGApp
from data_manager import DataManager

if __name__ == "__main__":
    root = tk.Tk()
    data_manager = DataManager()
    app = RPGApp(root, data_manager)
    root.mainloop()