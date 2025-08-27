import tkinter as tk
from tkinter import ttk, PhotoImage
from tkinter import *
from tkinter.font import Font
import os
import subprocess
from PIL import Image, ImageTk

class TouchMenuApp:#tamanho menu principal
    def __init__(self, root): 
        self.root = root
        self.root.title("Touch Menu Demo")
        self.root.geometry("1024x600")
        self.root.configure(bg="blue")
        self.root.resizable(True, True)
        self.root.minsize(width= 788, height = 588)

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ROMS_DIR = os.path.join(self.BASE_DIR, "ROMs")
        self.PLATAFORMAS = {
            "Super Nintendo": {
                "core": "snes9x",
                "roms": {
                    "Super Bomberman 4": os.path.join(self.ROMS_DIR, "snes", "Super Bomberman 4 (Japan).sfc")
                }
            },
            "Game Boy Advance": {
                "core": "mgba",
                "roms": {
                    "The Legend of Zelda": os.path.join(self.ROMS_DIR, "gb_advance", "Legend of Zelda, The - A Link to the Past & Four Swords (USA).gba")

                }
            }
        }
        
        # Configure styles
        self.setup_styles()
        
        # Create touch menu
        self.create_main_menu()

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
        main_frame = ttk.Frame(self.root, padding=20, style='Main.TFrame')
        main_frame.pack(expand=True, fill='both')
        
        button = ttk.Button( main_frame,
            image= self.load_icon("assets/gameboy.png", size=(170, 50)),
            command=lambda: self.menu_action("Game Boy"))
        button.place(relx=0.1, rely= 0.03)

        button2 = ttk.Button( main_frame, 
            image= self.load_icon("assets/supernintendo.png", size=(300,70)),
            command=lambda: self.menu_action("Super Nintendo"))
        button2.place(relx=0.1, rely=0.2)
        
        button3 = ttk.Button( main_frame, 
            image= self.load_icon("assets/gameboy_advance.png", size=(200,70)),
            command=lambda: self.menu_action("Game Boy Advance"))
        button3.place(relx=0.1, rely= 0.4)

        button4 = ttk.Button( main_frame, 
            image= self.load_icon("assets/MegaDrive.png", size=(270,70)),
            command=lambda: self.menu_action("Mega Drive"))
        button4.place(relx=0.1, rely=0.6)

        button5 = ttk.Button( main_frame, 
            image= self.load_icon("assets/playstation.png", size=(200,70)),
            command=lambda: self.menu_action("Playstation 1"))
        button5.place(relx=0.1, rely=0.8)
        
        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

    def menu_action(self, plataforma):
        if plataforma not in self.PLATAFORMAS:
            print(f"Plataforma {plataforma} não encontrada.")
            return

    # Fecha/limpa o menu anterior
        for widget in self.root.winfo_children():
            widget.destroy()

        frame_jogos = ttk.Frame(self.root, padding=20, style='Main.TFrame')
        frame_jogos.pack(expand=True, fill='both')

        label = ttk.Label(frame_jogos, text=f"Jogos - {plataforma}", font=self.big_font, background="#36b0e8", foreground="white")
        label.pack(pady=10)

        roms = self.PLATAFORMAS[plataforma]["roms"]

        for jogo, caminho_rom in roms.items():
            btn = ttk.Button(frame_jogos, text=jogo, style='Small.TButton',
                         command=lambda r=caminho_rom, p=plataforma: self.rodar_jogo(p, r))
            btn.pack(pady=5, fill='x')

    # Botão para voltar ao menu principal
        voltar_btn = ttk.Button(frame_jogos, text="⏪ Voltar", style='Small.TButton',
                            command=self.recriar_menu_principal)
        voltar_btn.pack(pady=20, fill='x')

    def rodar_jogo(self, plataforma, caminho_rom):
        retroarch_path = r"C:\Users\carla\Desktop\RetroArch\RetroArch-Win64\retroarch.exe"
        core = self.PLATAFORMAS[plataforma]["core"]

        try:
            subprocess.Popen([retroarch_path, "-L", core, caminho_rom])
            print(f"Iniciando {caminho_rom} no {plataforma}...")
        except Exception as e:
            print("Erro ao abrir jogo:", e)