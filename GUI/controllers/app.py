import tkinter as tk
from tkinter import ttk
from tkinter import * 
from tkinter.font import Font
from tkinter import Canvas
import os
import subprocess
from PIL import Image, ImageTk
import json

class TouchMenuApp:
    def __init__(self, root: Tk): 
        self.root = root
        self.root.title("Touch Menu Demo")
        self.root.geometry("1024x600")
        self.root.configure(bg="blue")
        self.root.resizable(True, True)
        self.root.minsize(width=788, height=588)
        self.canvas = Canvas(self.root, bg="blue", highlightthickness=0)
        
        # Game data storage
        self.games_data = {}
        self.current_console = None
        
        # Configure styles
        self.setup_styles()
        
        # Create main menu
        self.create_main_menu()
        
        # Load games data from JSON
        self.load_games_data("games.json")
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

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
        """Load game data from JSON file with console-based structure"""
        try:
            with open(json_file, 'r') as file:
                self.games_data = json.load(file)
            
            print("Games data loaded successfully")
            print(f"Loaded consoles: {list(self.games_data.keys())}")
            for console, games in self.games_data.items():
                print(f"{console}: {len(games)} games")
                
        except FileNotFoundError:
            print(f"Error: {json_file} not found")
            # Create empty data structure
            self.games_data = {
                "Super Nintendo": [],
                "Game Boy Advance": [],
                "Mega Drive": [],
                "Playstation 1": []
            }
        except json.JSONDecodeError as e:
            print(f"Error: {json_file} contains invalid JSON: {e}")
            self.games_data = {
                "Super Nintendo": [],
                "Game Boy Advance": [],
                "Mega Drive": [],
                "Playstation 1": []
            }

    def organize_games_by_console(self, raw_data):
        """Organize games by console based on file extension"""
        consoles = {
            "Super Nintendo": [".sfc", ".smc"],
            "Game Boy Advance": [".gba"],
            "Mega Drive": [".md", ".gen"],
            "Playstation 1": [".cue", ".bin", ".img"]
        }
        
        organized_data = {console: [] for console in consoles.keys()}
        
        for filename, game_info in raw_data.items():
            # Get file extension
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            # Find which console this game belongs to
            found_console = None
            for console, extensions in consoles.items():
                if ext in extensions:
                    found_console = console
                    break
            
            if found_console:
                # Add the game to the appropriate console list
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
            
            # Store reference to prevent garbage collection
            if not hasattr(self, '_icon_references'):
                self._icon_references = []
            self._icon_references.append(icon)
            
            return icon
        except Exception as e:
            print(f"Erro ao carregar {icon_path}: {e}")
            return None

    def create_main_menu(self):
        # Clear the current frame
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
        
        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

    def menu_action(self, item):
        print(f"Selected: {item}")
        # Visual feedback
        self.root.configure(background='#2ecc71')
        self.root.after(200, lambda: self.root.configure(background='#ecf0f1'))
        
        # Store the current console selection
        self.current_console = item
        
        # Show games for the selected console
        self.show_games_for_console(item)
        
    def show_games_for_console(self, console_name):
        """Display games for the selected console with scrollbar"""
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Back button
        back_button = ttk.Button(main_frame, text="← Back to Main Menu", 
                                command=self.create_main_menu)
        back_button.grid(row=0, column=0, sticky="nw", pady=(0, 20))
        
        # Title
        title_label = ttk.Label(main_frame, text=f"{console_name} Games", 
                            font=self.big_font, background="#36b0e8")
        title_label.grid(row=0, column=1, columnspan=2, pady=(0, 20))
        
        # Create a canvas with scrollbar for games
        canvas = tk.Canvas(main_frame, bg="#36b0e8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Main.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, columnspan=3, sticky="nsew")
        scrollbar.grid(row=1, column=3, sticky="ns")
        
        # Configure grid weights
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Check if we have games for this console
        if console_name in self.games_data and self.games_data[console_name]:
            games = self.games_data[console_name]
            
            # Display games in a grid within the scrollable frame
            # Display games in a grid within the scrollable frame - VERTICAL LAYOUT
            max_rows = 6  # Fixed number of rows per column
            row, col = 0, 0

            for i, game in enumerate(games):
                # Create a button for each game
                game_button = ttk.Button(
                    scrollable_frame,
                    text=game["name"],
                    style='Small.TButton',
                    command=lambda g=game: self.launch_game(g)
                )
                game_button.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                
                # Update grid position - VERTICAL FIRST
                row += 1
                if row >= max_rows:
                    row = 0
                    col += 1
            
            # Configure grid weights for responsive layout
            for i in range(max_rows):
                scrollable_frame.grid_columnconfigure(i, weight=1)
        else:
            # No games found for this console
            no_games_label = ttk.Label(scrollable_frame, 
                                    text="No games found for this console.",
                                    font=self.big_font, 
                                    background="#36b0e8")
            no_games_label.grid(row=0, column=0, columnspan=3, pady=50)
    
    # Make mouse wheel scroll work
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def launch_game(self, game):
        """Launch the selected game with better error handling"""
        print(f"Launching: {game['name']}")
        
        core_path = game["core"]
        rom_path = game["path"]
        
        try:
            # Visual feedback
            self.root.configure(background='green')
            self.root.update()
            
            command = ["retroarch"]
            if core_path and os.path.exists(core_path):
                command.extend(["-L", core_path])
            command.append(rom_path)
            
            print(f"Running command: {' '.join(command)}")
            
            # Launch the game (non-blocking)
            subprocess.Popen(command)
            
            # Return to normal background after a delay
            self.root.after(1000, lambda: self.root.configure(background='blue'))
            
        except FileNotFoundError:
            print(f"Error: retroarch not found or game file missing")
            self.root.configure(background='red')
            self.root.after(1000, lambda: self.root.configure(background='blue'))
        except Exception as e:
            print(f"Error launching game: {e}")
            self.root.configure(background='red')
            self.root.after(1000, lambda: self.root.configure(background='blue'))