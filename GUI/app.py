import tkinter as tk
from tkinter import ttk, PhotoImage
from tkinter.font import Font
import os
import subprocess

class TouchMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Touch Menu Demo")
        self.root.geometry("1024x600")  # Common tablet size
        
        # Create touch menu
        self.create_main_menu()

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
        main_frame = ttk.Frame(self.root, width=0.0125)
        main_frame.pack(expand=True, fill='both')
        
        # Row 1
        button = ttk.Button(
            main_frame,
            image=self.load_icon("assets/retroarch.png"),
            compound='top',
            text="RetroArch",
            command=lambda: self.menu_action("Home"),
            width=0.25,
        )
        button.pack()
        
    def menu_action(self, item):
        """Handle menu selection with visual feedback"""
        print(f"Selected: {item}")
        home = os.path.expanduser("~")
        core_path = os.path.join(home, ".config/retroarch/cores/mupen64plus_next_libretro.so")
        rom_path = os.path.join(home, "Downloads/Yuke Yuke!! Trouble Makers (J) [!].n64")
        subprocess.run([
            "retroarch",
            "-L", core_path,
            rom_path
        ])

