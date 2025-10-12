import tkinter as tk
from tkinter import ttk, Canvas
from tkinter.font import Font
import os
import subprocess
import json
import pygame

from .remapper_gui import ControllerRemapperFrame

class TouchMenuApp:
    def __init__(self, root: tk.Tk): 
        self.root = root
        self.root.title("Touch Menu")
        self.root.geometry("1024x600")
        self.root.configure(bg="#36b0e8")
        self.root.resizable(True, True)
        self.root.minsize(width=788, height=588)
        
        self.joystick = None
        self.held_shoulder_buttons = set()
        self.SHOULDER_BUTTONS = {4, 5, 6, 7} # L1, R1, L2, R2
        self.STICK_BUTTONS = {10, 11} # L3, R3

        # ### NEW: State management for menu navigation ###
        self.navigable_widgets = [] # List of buttons on the current page
        self.current_focus_index = -1 # Index of the currently "selected" button
        self.last_nav_time = 0 # For debouncing D-pad input
        self.NAV_DEBOUNCE_MS = 180 # Cooldown between navigation inputs (in milliseconds)
        # ### NEW: END ###

        self.games_data = {}
        self.load_games_data("games.json")
        
        self.setup_styles()
        
        container = ttk.Frame(self.root, style='Main.TFrame')
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainMenuFrame, GameListFrame, ControllerRemapperFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenuFrame")
        self._initialize_gamepad_listener()

    # ### NEW: Method to register which buttons can be navigated on the current screen ###
    def register_navigable_widgets(self, widgets: list):
        """Sets the list of widgets for controller navigation on the current frame."""
        self.navigable_widgets = widgets
        # If there are any navigable widgets, set focus to the first one
        if self.navigable_widgets:
            self._update_focus(old_index=-1, new_index=0)
        else:
            self.current_focus_index = -1
    # ### NEW: END ###
            
    def show_frame(self, page_name, console_name=None):
        """Raises the requested frame to the top and prepares it for navigation."""
        frame = self.frames[page_name]
        if page_name == "GameListFrame" and console_name:
            frame.set_console(console_name)
            frame.generate_game_list()
        
        frame.tkraise()
        # ### NEW: After showing a frame, register its buttons for navigation ###
        # We call a method on the frame itself to get its buttons.
        if hasattr(frame, 'get_navigable_widgets'):
            self.register_navigable_widgets(frame.get_navigable_widgets())
        else:
            self.register_navigable_widgets([]) # Clear navigation for this frame
    # ### NEW: END ###

    def _initialize_gamepad_listener(self):
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"✅ Gamepad '{self.joystick.get_name()}' connected.")
            self._poll_gamepad_events()
        else:
            print("⚠️ No gamepad connected.")

    def _poll_gamepad_events(self):
        """Checks for pygame events for both shortcuts and menu navigation."""
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            # --- Return-to-home shortcut logic (unchanged) ---
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in self.SHOULDER_BUTTONS:
                    self.held_shoulder_buttons.add(event.button)
                if event.button in self.STICK_BUTTONS and self.SHOULDER_BUTTONS.issubset(self.held_shoulder_buttons):
                    self.show_frame("MainMenuFrame")
                
                # ### NEW: Handle "Select" button press (X button is usually button 0) ###
                if event.button == 0 and self.current_focus_index != -1:
                    focused_widget = self.navigable_widgets[self.current_focus_index]
                    print(f"Controller selected: {focused_widget.cget('text')}")
                    focused_widget.invoke() # Programmatically "click" the button
                # ### NEW: END ###

            elif event.type == pygame.JOYBUTTONUP:
                if event.button in self.SHOULDER_BUTTONS:
                    self.held_shoulder_buttons.discard(event.button)
            
            # ### NEW: Handle D-Pad navigation ###
            elif event.type == pygame.JOYHATMOTION:
                # event.value is a tuple (x, y); e.g., (0, 1) is UP, (0, -1) is DOWN
                hat_x, hat_y = event.value
                # Debounce to prevent rapid scrolling
                if current_time - self.last_nav_time > self.NAV_DEBOUNCE_MS:
                    if hat_y == 1: # D-Pad UP
                        self._navigate_menu(-1)
                        self.last_nav_time = current_time
                    elif hat_y == -1: # D-Pad DOWN
                        self._navigate_menu(1)
                        self.last_nav_time = current_time
            # ### NEW: END ###

        self.root.after(20, self._poll_gamepad_events) # Poll more frequently for responsiveness

    # ### NEW: Methods for managing focus ###
    def _navigate_menu(self, direction: int):
        """Move the focus up or down in the widget list."""
        if not self.navigable_widgets:
            return

        # Calculate the new index, wrapping around if necessary
        old_index = self.current_focus_index
        new_index = (old_index + direction) % len(self.navigable_widgets)
        
        self._update_focus(old_index, new_index)

    def _update_focus(self, old_index: int, new_index: int):
        """Update the visual style of the buttons to show focus."""
        # Remove focus from the old widget, if it exists
        if old_index != -1 and old_index < len(self.navigable_widgets):
            widget = self.navigable_widgets[old_index]
            # Infer original style from the widget's text
            original_style = 'Remapper.TButton' if "CONFIGURE" in widget.cget('text') else 'Small.TButton'
            widget.configure(style=original_style)

        # Apply focus to the new widget
        if new_index != -1 and new_index < len(self.navigable_widgets):
            widget = self.navigable_widgets[new_index]
            widget.configure(style='Focus.TButton')
            self.current_focus_index = new_index
    # ### NEW: END ###

    def setup_styles(self):
        self.big_font = Font(family='Helvetica', size=24, weight='bold')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Main.TFrame', background="#36b0e8")
        self.style.configure('TLabel', background='#36b0e8', foreground='white', font=('Helvetica', 14, 'bold'))
        self.style.configure(
            'Small.TButton', font=('Helvetica', 16, 'bold'), foreground='white',
            background='#007BFF', padding=(20, 10), relief='raised', borderwidth=5
        )
        self.style.map('Small.TButton', background=[('active', '#0056b3')])
        self.style.configure(
            'Remapper.TButton', font=('Helvetica', 18, 'bold'), foreground='black',
            background='#FFC107', padding=(25, 12), relief='raised', borderwidth=5
        )
        self.style.map('Remapper.TButton', background=[('active', '#E0A800')])
        
        # ### NEW: Style for the visually focused button ###
        self.style.configure(
            'Focus.TButton', font=('Helvetica', 18, 'bold'), foreground='black',
            background='#52D171', padding=(25, 12), relief='raised', borderwidth=5,
            bordercolor='white'
        )
        # ### NEW: END ###
        
    def load_games_data(self, json_path):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        full_path = os.path.join(base_dir, json_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r') as f:
                    self.games_data = json.load(f)
            except Exception as e:
                print(f"Error reading games.json: {e}")
        else:
            print(f"JSON file not found at: {full_path}")

    def launch_game(self, game):
        print(f"Launching: {game['name']}")
        core_path, rom_path = game.get("core"), game.get("path")
        try:
            command = ["retroarch"]
            if core_path and os.path.exists(core_path):
                command.extend(["-L", core_path])
            command.append(rom_path)
            subprocess.Popen(command)
        except Exception as e:
            print(f"Error launching game: {e}")

class MainMenuFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style='Main.TFrame')
        self.controller = controller
        # ### NEW: Store buttons for navigation ###
        self.navigable_buttons = []

        ttk.Label(self, text="Select Console or Configure", font=controller.big_font).pack(pady=40)
        
        remapper_btn = ttk.Button(self, text="🎮 CONFIGURE GAMEPAD ⌨️",
                   command=lambda: controller.show_frame("ControllerRemapperFrame"), 
                   style='Remapper.TButton')
        remapper_btn.pack(pady=30, padx=50)
        self.navigable_buttons.append(remapper_btn)

        self.console_container = ttk.Frame(self, style='Main.TFrame')
        self.console_container.pack(pady=20)
        
        self.generate_console_buttons()

    # ### NEW: Expose the list of buttons to the main controller ###
    def get_navigable_widgets(self):
        return self.navigable_buttons

    def generate_console_buttons(self):
        for widget in self.console_container.winfo_children():
            widget.destroy()
        
        # ### NEW: Clear and repopulate the console buttons in the navigation list ###
        # We keep the remapper button and add the console buttons after it.
        self.navigable_buttons = self.navigable_buttons[:1]

        consoles = self.controller.games_data.keys()
        if not consoles:
            ttk.Label(self.console_container, text="No consoles found in games.json.").pack()
            return
            
        for console_name in consoles:
            btn = ttk.Button(self.console_container, text=console_name, 
                       command=lambda c=console_name: self.controller.show_frame("GameListFrame", console_name=c),
                       style='Small.TButton')
            btn.pack(side=tk.LEFT, padx=10, pady=10)
            self.navigable_buttons.append(btn)

class GameListFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style='Main.TFrame')
        self.controller = controller
        self.console_name = None
        # ### NEW: Store buttons for navigation ###
        self.navigable_buttons = []
        
        self.header_label = ttk.Label(self, text="", font=controller.big_font)
        self.header_label.pack(pady=10)

        self.list_frame = ttk.Frame(self, style='Main.TFrame')
        self.list_frame.pack(pady=10, padx=50, fill="x")

        back_btn = ttk.Button(self, text="← Back to Consoles",
                   command=lambda: controller.show_frame("MainMenuFrame"), 
                   style='Small.TButton')
        back_btn.pack(pady=20)
        # ### NEW: The back button is also navigable ###
        self.back_button = back_btn

    # ### NEW: Expose the list of buttons to the main controller ###
    def get_navigable_widgets(self):
        return self.navigable_buttons

    def set_console(self, console_name):
        self.console_name = console_name
        self.header_label.config(text=f"Games - {console_name}")

    def generate_game_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        # ### NEW: Clear and repopulate the game buttons in the navigation list ###
        self.navigable_buttons.clear()
        
        if not self.console_name: return

        for game in self.controller.games_data.get(self.console_name, []):
            btn = ttk.Button(self.list_frame, text=game['name'], 
                       command=lambda g=game: self.controller.launch_game(g),
                       style='Small.TButton')
            btn.pack(fill='x', pady=5)
            self.navigable_buttons.append(btn)
        
        # Add the back button to the end of the navigation list
        self.navigable_buttons.append(self.back_button)