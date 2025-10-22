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
        self.root.geometry("1024x600") #colocar tela inteira
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
        
        # Inicializa o menu principal
        self.show_platform_menu()

    # Troca para o menu de plataformas
    def show_platform_menu(self):
        self.clear_window()
        self.current_menu = MenuPlataformas(self)

    # Troca para o menu de jogos
    def show_game_menu(self, plataforma):
        self.clear_window()
        self.current_menu = MenuJogos(self, plataforma)

    # Remove todos os widgets antes de criar outro frame
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


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

        ttk.Label(self.scroll_frame, text="Selecione a Plataforma", font=app.big_font,
                  background="#36b0e8", foreground="white").pack(pady=20, padx=300)

        # Cria botões com imagem
        for nome, dados in app.PLATAFORMAS.items():
            icon = self.load_icon(dados["icon"], size=(250, 70))
            btn = ttk.Button(self.scroll_frame, 
                             image=icon, 
                             style='Small.TButton', 
                             command=lambda n=nome: app.show_game_menu(n))
            btn.image = icon  # evitar garbage collection
            btn.pack(pady=10, anchor='center')

    def load_icon(self, path, size=(100, 100)):
        if not os.path.exists(path):
            print(f"Ícone não encontrado: {path}")
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