from tkinter import ttk, PhotoImage
import os
import subprocess
from typing import Dict, List

class TouchMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Touch Menu Demo")
        self.root.geometry("1024x600")  # Common tablet size
        
        self.games = {
            "Trouble Makers": {
                "icon": "assets/retroarch.png",
                "core": "mupen64plus_next_libretro.so",
                "rom": "Yuke Yuke!! Trouble Makers (J) [!].n64"
            },
            "Super Mario 64": {
                "icon": "assets/retroarch.png",  
                "core": "mupen64plus_next_libretro.so",
                "rom": "Super Mario 64 (U) [!].n64"
            },
            "Zelda OOT": {
                "icon": "assets/retroarch.png", 
                "core": "mupen64plus_next_libretro.so",
                "rom": "Legend of Zelda, The - Ocarina of Time (U) [!].n64"
            }
        }

        # Create touch menu
        self.create_main_menu()

    def load_icon(self, icon_path):
        """Load an icon from file with proper error handling"""
        
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
        

    def create_main_menu(self):
        """Create touch-friendly menu grid"""
        
        cols=3
        row=3
        main_frame = ttk.Frame(self.root)
        main_frame.pack()

        for i, (game_name, game_config) in enumerate(self.games.items()):
            row = i // cols  # Calculate row position
            col = i % cols
            
            icon = self.load_icon(game_config["icon"])
            

            button = ttk.Button(
            main_frame,
            image=icon,
            compound='top',
            text=game_name,
            command=lambda g=game_name, r=game_config["rom"], c=game_config["core"]: self.menu_action(game=r, core=c),
            style='Game.TButton'
            )
            button.grid(
            row=row,
            column=col,
            padx=10,
            pady=10,
            sticky='nsew'
            )
        
    def menu_action(self, game, core):
        home = os.path.expanduser("~")
        core_path = os.path.join(home, ".config/retroarch/cores/", core)
        print(core_path)
        rom_path = os.path.join(home, "Downloads/", game)
        print(rom_path)
        subprocess.run([
            "retroarch",
            "-L", core_path,
            rom_path
        ])

