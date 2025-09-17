import tkinter as tk
from tkinter import ttk, PhotoImage
from tkinter import *
from tkinter.font import Font
import os
import subprocess
from PIL import Image, ImageTk
import json

class TouchMenuApp:
    def __init__(self, root): 
        self.root = root
        self.root.title("Touch Menu Demo")
        self.root.geometry("1024x600")
        self.root.configure(bg="blue")
        self.root.resizable(True, True)
        self.root.minsize(width=788, height=588)
        
        # Game data storage
        self.games_data = {}
        self.current_console = None
        
        # Configure styles
        self.setup_styles()
        
        # Create main menu
        self.create_main_menu()
        
        # Load games data from JSON
        self.load_games_data("games.json")

    def setup_styles(self):
        """Configure touch-friendly styles"""
        self.big_font = Font(family='Helvetica', size=24, weight='bold')
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

        self.style.configure('Main.TFrame', background="#36b0e8")
    
        self.style.configure(
            'Small.TButton',
            font=self.big_font,
            padding=30,
            relief='flat',
            foreground='white')
        
        self.style.map('Small.TButton',background=[('active', '#2980b9'), ('pressed', '#1c638e')])
  
    def load_games_data(self, json_file):
        try:
            with open(json_file, 'r') as file:
                raw_data = json.load(file)

            self.games_data = self.organize_games_by_console(raw_data)
            
            print("Games data loaded successfully")
        except FileNotFoundError:
            print(f"Error: {json_file} not found")
        except json.JSONDecodeError:
            print(f"Error: {json_file} contains invalid JSON")

    def organize_games_by_console(self, raw_data):
   
        consoles = {
            "Super Nintendo": [".sfc", ".smc"],
            "Game Boy Advance": [".gba"],
            "Mega Drive": [".md", ".gen"],
            "Playstation 1": [".cue", ".bin", ".img"]
        }
        
        organized_data = {console: [] for console in consoles.keys()}
        
        for filename, game_info in raw_data.items():
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            found_console = None
            for console, extensions in consoles.items():
                if ext in extensions:
                    found_console = console
                    break
            
            if found_console:
                organized_data[found_console].append({
                    "name": game_info["name"],
                    "path": game_info["path"],
                    "core": game_info["core"]
                })
        
        return organized_data
    def load_icon(self, icon_path, size=(100,100)):
        try:
            if not os.path.exists(icon_path):
                raise FileNotFoundError(f"Icon not found: {icon_path}")
                
            img = Image.open(icon_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            icon = ImageTk.PhotoImage(img)
            
            if not hasattr(self, '_icon_references'):
                self._icon_references = []
            self._icon_references.append(icon)
            
            return icon
        except Exception as e:
            print(f"Erro ao carregar {icon_path}: {e}")
            return None

    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        main_frame = ttk.Frame(self.root, padding=20, style='Main.TFrame')
        main_frame.pack(expand=True, fill='both')
        
        button = ttk.Button(main_frame,
            image=self.load_icon("assets/gameboy.png", size=(170, 50)),
            command=lambda: self.menu_action("Home"))
        button.place(relx=0.1, rely=0.03)

        button2 = ttk.Button(main_frame, 
            image=self.load_icon("assets/supernintendo.png", size=(300,70)),
            command=lambda: self.menu_action("Super Nintendo"))
        button2.place(relx=0.1, rely=0.2)
        
        button3 = ttk.Button(main_frame, 
            image=self.load_icon("assets/gameboy_advance.png", size=(200,70)),
            command=lambda: self.menu_action("Game Boy Advance"))
        button3.place(relx=0.1, rely=0.4)

        button4 = ttk.Button(main_frame, 
            image=self.load_icon("assets/MegaDrive.png", size=(270,70)),
            command=lambda: self.menu_action("Mega Drive"))
        button4.place(relx=0.1, rely=0.6)

        button5 = ttk.Button(main_frame, 
            image=self.load_icon("assets/playstation.png", size=(200,70)),
            command=lambda: self.menu_action("Playstation 1"))
        button5.place(relx=0.1, rely=0.8)
        
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

    def menu_action(self, item):
        print(f"Selected: {item}")
        self.root.configure(background='#2ecc71')
        self.root.after(200, lambda: self.root.configure(background='#ecf0f1'))
        
        self.current_console = item
        
        self.show_games_for_console(item)
        
    def show_games_for_console(self, console_name):
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        games_frame = ttk.Frame(self.root, padding=20, style='Main.TFrame')
        games_frame.pack(expand=True, fill='both')
        
        back_button = ttk.Button(games_frame, text="← Back", 
                                command=self.create_main_menu)
        back_button.grid(row=0, column=0, sticky="nw", pady=(0, 20))
        
        title_label = ttk.Label(games_frame, text=f"{console_name} Games", 
                               font=self.big_font, background="#36b0e8")
        title_label.grid(row=0, column=1, columnspan=2, pady=(0, 20))
        
        if console_name in self.games_data:
            games = self.games_data[console_name]
            
            row, col = 1, 0
            max_cols = 3 
            
            for game in games:
                game_button = ttk.Button(
                    games_frame,
                    text=game["name"],
                    style='Small.TButton',
                    command=lambda g=game: self.launch_game(g)
                )
                game_button.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            for i in range(max_cols):
                games_frame.grid_columnconfigure(i, weight=1)
            for i in range(row + 1):
                games_frame.grid_rowconfigure(i, weight=1)
        else:
            # No games found for this console
            no_games_label = ttk.Label(games_frame, text="No games found for this console.",
                                      font=self.big_font, background="#36b0e8")
            no_games_label.grid(row=1, column=0, columnspan=3, pady=50)
    
    def launch_game(self, game):
        """Launch the selected game"""
        print(f"Launching: {game['name']}")
        
        retroarch_path = "retroarch"
        core_path = game["core"]  
        rom_path = game["path"]
        print(core_path, rom_path)
        try:
            if core_path:
                subprocess.run([retroarch_path, "-L", core_path, rom_path])
            else:
                subprocess.run([retroarch_path, rom_path])
        except Exception as e:
            print(f"Error launching game: {e}")

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = TouchMenuApp(root)
    root.mainloop()