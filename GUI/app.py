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
        self.root.geometry("1024x600")
        self.root.configure(bg="blue")
        self.root.resizable(True, True) #false
        self.root.minsize(width= 788, height = 588)

        self.big_font = Font(family='Helvetica', size=24, weight='bold')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Main.TFrame', background="#36b0e8")
        self.style.configure('Small.TButton', font=self.big_font, padding=30, relief='flat', foreground='white')
        self.style.map('Small.TButton', background=[('active', '#2980b9'), ('pressed', '#1c638e')])

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ROMS_DIR = os.path.join(self.BASE_DIR, "ROMs")
        self.ASSETS_DIR = os.path.join(self.BASE_DIR, "assets")
        #dicionário deve ser mais dinâmico. A pasta de ROMs deve ficar oculta
        self.PLATAFORMAS = { 
            "Super Nintendo": {
                "core": "snes9x",
                "icon": os.path.join(self.ASSETS_DIR, "supernintendo.png"),
                "roms": {
                    "Super Bomberman 4": os.path.join(self.ROMS_DIR, "snes", "Super Bomberman 4 (Japan).sfc"),
                    "Donkey Kong Country": os.path.join(self.ROMS_DIR, "snes", "Donkey Kong Country.smc"),
                    "Final Fantasy II (PT-BR)": os.path.join(self.ROMS_DIR, "snes", "Final Fantasy II [BR].smc"),
                    "Home Alone": os.path.join(self.ROMS_DIR, "snes", "Home Alone.smc"),
                    "Super Mario World (PT-BR)": os.path.join(self.ROMS_DIR, "snes", "Super Mario World [BR].smc"),
                }
            },
            "Game Boy Advance": {
                "core": "mgba",
                "icon": os.path.join(self.ASSETS_DIR, "gba.png"),
                "roms": {
                    "The Legend of Zelda": os.path.join(self.ROMS_DIR, "gb_advance", "Legend of Zelda, The - A Link to the Past & Four Swords (USA).gba"),
                    "Final Fantasy IV Advance": os.path.join(self.ROMS_DIR, "gb_advance", "Final Fantasy IV Advance.gba"),
                    "Metal Gear Solid": os.path.join(self.ROMS_DIR, "gb_advance", "Metal Gear Solid.gbc"),
                    "Pokemon - Emerald Version": os.path.join(self.ROMS_DIR, "gb_advance", "Pokemon - Emerald Version.gba"),
                    "Tony Hawk's Pro Skater 4": os.path.join(self.ROMS_DIR, "gb_advance", "Tony Hawk's Pro Skater 4.gba")

                }
            },
            "Game Boy": {
                "core": "sameboy",
                "icon": os.path.join(self.ASSETS_DIR, "gameboy.png"),
                "roms": {
                    "Pokemon - Red Version": os.path.join(self.ROMS_DIR, "gameboy", "Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb"),
                }
            },
            "Mega Drive": {
                "core": "picodrive",
                "icon": os.path.join(self.ASSETS_DIR, "MegaDrive.png"),
                "roms": {
                    "Alex Kidd in the Enchanted Castle": os.path.join(self.ROMS_DIR, "megadrive", "Alex Kidd in the Enchanted Castle.smd"),
                    "Sonic The Hedgegod": os.path.join(self.ROMS_DIR, "megadrive", "Sonic The Hedgehog (USA, Europe).md"),
                    "Donald Duck in Maui Mallard": os.path.join(self.ROMS_DIR, "megadrive", "Donald Duck in Maui Mallard.smd"),
                    "Batman Returns": os.path.join(self.ROMS_DIR, "megadrive", "Batman Returns.smd"),
                    "Addams Family Values": os.path.join(self.ROMS_DIR, "megadrive", "Addams Family Values.smd"),
                }
            }
        }
        
        self.show_platform_menu()

    def show_platform_menu(self):
        self.clear_window()
        self.current_menu = MenuPlataformas(self)

    def show_game_menu(self, plataforma):
        self.clear_window()
        self.current_menu = MenuJogos(self, plataforma)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

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
        
        self.style.map('Small.TButton',background=[('active', "#f9f9f9"), ('pressed', '#1c638e')])

class MenuPlataformas:
    def __init__(self, app):
        self.app = app

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

        label_titulo = ttk.Label(self.scroll_frame, 
                  text="Selecione uma plataforma", 
                  font=app.big_font,
                  background="#36b0e8", 
                  anchor='center',
                  foreground="white")
        label_titulo.pack(pady=30)
       
        center_frame = ttk.Frame(self.scroll_frame, style='Main.TFrame')
        center_frame.pack(expand=True)

        # Cria botões com imagem
        for nome, dados in app.PLATAFORMAS.items():
            icon = self.load_icon(dados["icon"], size=(270, 70))
            plataforma = ttk.Button(center_frame, 
                             image=icon, 
                             style='Small.TButton',
                             compound='center', 
                             command=lambda n=nome: app.show_game_menu(n))
            plataforma.image = icon  
            plataforma.pack(pady=20)

        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )

    def load_icon(self, path, size=(100,100)):
        if not os.path.exists(path):
            print(f"Erro ao carregar {path}")
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


        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

                
        voltar = ttk.Button(self.canvas, 
                   text="⬅ Voltar", 
                   style='Small.TButton',
                   command=app.show_platform_menu,
                   padding=(5,15))
        voltar.pack(anchor='w', padx=30, pady=(20,10))

        titulo = ttk.Label(self.scroll_frame, text=f"Jogos - {plataforma}", 
                  font=app.big_font,
                  background="#36b0e8", 
                  foreground="white")
        titulo.pack(pady=20)

        roms = app.PLATAFORMAS[plataforma]["roms"]

        for jogo, caminho in roms.items():
            game = ttk.Button(self.scroll_frame, 
                             text=jogo, 
                             style='Small.TButton',
                             command=lambda r=caminho: self.launch_game(r))
            game.pack(pady=10, fill='x', padx=100)     
        
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )

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