games = {
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

for i, (game_name, game) in enumerate(games.items()):
    print(game["rom"])