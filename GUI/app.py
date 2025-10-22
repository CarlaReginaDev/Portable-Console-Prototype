import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
import os
import subprocess
from PIL import Image, ImageTk



class TouchMenuApp:#tamanho menu principal
    def __init__(self, root): 
        self.root = root
        self.root.title("Menu Principal")
        self.root.attributes("-fullscreen", True)
        self.root.bind('<Escape>', self.sair_tela)
        self.root.configure(bg="blue")

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ROMS_DIR = os.path.join(self.BASE_DIR, "ROMs")
        self.ASSETS_DIR = os.path.join(self.BASE_DIR, "assets")
        #dicionário deve ser mais dinâmico. A pasta de ROMs deve ficar oculta
        self.PLATAFORMAS = { 
            "Super Nintendo": {
                "core": "snes9x",
                "icon": os.path.join(self.ASSETS_DIR, "supernintendo.png"),
                "roms": {
                    "Super Bomberman 4": os.path.join(self.ROMS_DIR, "snes", "Super Bomberman 4 (Japan).sfc")
                }
            },
            "Game Boy Advance": {
                "core": "mgba",
                "icon": os.path.join(self.ASSETS_DIR, "gameboy_advance.png"),
                "roms": {
                    "The Legend of Zelda": os.path.join(self.ROMS_DIR, "gb_advance", "Legend of Zelda, The - A Link to the Past & Four Swords (USA).gba")

                }
            },
            "Game Boy": {
                "core": "sameboy",
                "icon": os.path.join(self.ASSETS_DIR, "gameboy.png"),
                "roms": {
                    "Pokemon - Red Version": os.path.join(self.ROMS_DIR, "gameboy", "Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb")
                }
            },
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
        img = Image.open(path)
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)


class MenuJogos:
    def __init__(self, app, plataforma):
        self.app = app
        self.plataforma = plataforma

        # Frame principal com rolagem
        self.canvas = tk.Canvas(app.root, bg="#36b0e8", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(app.root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas, style='Main.TFrame')

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        ttk.Label(self.scroll_frame, text=f"Jogos - {plataforma}", font=app.big_font,
                  background="#36b0e8", foreground="white").pack(pady=20)

        roms = app.PLATAFORMAS[plataforma]["roms"]

        for jogo, caminho in roms.items():
            btn = ttk.Button(self.scroll_frame, 
                             text=jogo, 
                             style='Small.TButton',
                             command=lambda r=caminho: self.launch_game(r))
            btn.pack(pady=10, fill='x', padx=100)

        ttk.Button(self.scroll_frame, text="⬅ Voltar", style='Small.TButton',
                   command=app.show_platform_menu).pack(pady=20)

    def launch_game(self, rom_path):
        retroarch_path = r"C:\Users\carla\Desktop\RetroArch\RetroArch-Win64\retroarch.exe"
        core = self.app.PLATAFORMAS[self.plataforma]["core"]

        try:
            subprocess.Popen([retroarch_path, "-L", core, rom_path])
            print(f"Abrindo {rom_path} com núcleo {core}")
        except Exception as e:
            print("Erro ao abrir RetroArch:", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = TouchMenuApp(root)
    root.mainloop()