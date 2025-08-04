import tkinter as tk
from tkinter import ttk

from controllers.app import TouchMenuApp

root = tk.Tk()
app = TouchMenuApp(root)

root.mainloop()