import tkinter as tk
from tkinter import ttk, PhotoImage
from tkinter.font import Font
import os

class TouchMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Touch Menu Demo")
        self.root.geometry("1024x600")  # Common tablet size
        
        # Configure styles
        self.setup_styles()
        
        # Load icons (replace with your own PNGs)
        self.load_icon("assets/retroarch.png")
        
        # Create touch menu
        self.create_main_menu()

    def setup_styles(self):
        """Configure touch-friendly styles"""
        self.big_font = Font(family='Helvetica', size=24, weight='bold')
        self.button_style = ttk.Style()
        self.button_style.configure(
            'Small.TButton',
            font=self.big_font,
            padding=30,
            relief='flat',
            background='#3498db',
            foreground='white'
        )
        self.button_style.map(
            'Big.TButton',
            background=[('active', '#2980b9'), ('pressed', '#1c638e')]
        )

    def load_icon(self, icon_path):
        """Load an icon from file with proper error handling"""
        try:
            # Check if file exists first
            if not os.path.exists(icon_path):
                raise FileNotFoundError(f"Icon not found: {icon_path}")
                
            # Load the image
            icon = PhotoImage(file=icon_path)
            
            # Store reference to prevent garbage collection
            if not hasattr(self, '_icon_references'):
                self._icon_references = []
            self._icon_references.append(icon)
            
            return icon
            
        except Exception as e:
            print(f"Error loading icon {icon_path}: {str(e)}")
            # Return a fallback icon
            return self.create_fallback_icon("!")

    def create_main_menu(self):
        """Create touch-friendly menu grid"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Row 1
        button = ttk.Button(
            main_frame,
            image=self.load_icon("assets/retroarch.png"),
            style='Small.TButton',
            compound='top',
            text="RetroArch",
            command=lambda: self.menu_action("Home")
        )
        button.place(relheight=0.005,relwidth=0.005, relx=2, rely=5)
        button.pack()
        
        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

    def menu_action(self, item):
        """Handle menu selection with visual feedback"""
        print(f"Selected: {item}")
        # Visual feedback (change button color temporarily)
        self.root.configure(background='#2ecc71')
        self.root.after(200, lambda: self.root.configure(background='#ecf0f1'))

