"""
Script to convert a text file list of games to JSON format for the TouchMenuApp
"""

import json
import os
import argparse
from pathlib import Path

def get_core_for_extension(extension: str):
    """Map file extensions to RetroArch cores"""
    core_mapping = {
        '.sfc': '/home/kleber/.config/retroarch/cores/snes9x_libretro.so',
        '.smc': '/home/kleber/.config/retroarch/cores/snes9x_libretro.so',
        '.gba': '/home/kleber/.config/retroarch/cores/mgba_libretro.so',
        '.gb': '/home/kleber/.config/retroarch/cores/gambatte_libretro.so',
        '.gbc': '/home/kleber/.config/retroarch/cores/gambatte_libretro.so',
        '.md': '/home/kleber/.config/retroarch/cores/genesis_plus_gx_libretro.so',
        '.gen': '/home/kleber/.config/retroarch/cores/genesis_plus_gx_libretro.so',
        '.cue': '/home/kleber/.config/retroarch/cores/pcsx_rearmed_libretro.so',
        '.bin': '/home/kleber/.config/retroarch/cores/pcsx_rearmed_libretro.so',
        '.img': '/home/kleber/.config/retroarch/cores/pcsx_rearmed_libretro.so',
        '.nes': '/home/kleber/.config/retroarch/cores/fceumm_libretro.so',
        '.nds': '/home/kleber/.config/retroarch/cores/desmume_libretro.so',
        '.iso': '/home/kleber/.config/retroarch/cores/pcsx_rearmed_libretro.so'
    }
    return core_mapping.get(extension.lower(), '')

def get_console_for_extension(extension: str):
    """Map file extensions to console names"""
    console_mapping = {
        '.sfc': 'Super Nintendo',
        '.smc': 'Super Nintendo',
        '.gba': 'Game Boy Advance',
        '.gb': 'Game Boy',
        '.gbc': 'Game Boy Color',
        '.md': 'Mega Drive',
        '.gen': 'Mega Drive',
        '.cue': 'Playstation 1',
        '.bin': 'Playstation 1',
        '.img': 'Playstation 1',
        '.iso': 'Playstation 1',
        '.nes': 'Nintendo Entertainment System',
        '.nds': 'Nintendo DS'
    }
    return console_mapping.get(extension.lower(), 'Other')

def parse_txt_file(txt_file_path, games_directory):
    """
    Parse a text file containing game names and convert to JSON structure
    
    Expected TXT format (one game per line):
    Super Mario World (USA).sfc
    Donkey Kong Country.sfc
    Sonic The Hedgehog.md
    """
    games_data = {}
    
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            
            filename = line
            name, ext = os.path.splitext(filename)
            
            console = get_console_for_extension(ext)
            core = get_core_for_extension(ext)
            path = os.path.join(games_directory, filename)
            
            if console not in games_data:
                games_data[console] = []
            
            game_info = {
                "name": name,
                "path": path,
                "core": core
            }
            
            games_data[console].append(game_info)
            print(f"Added: {name} ({console})")
    
    except FileNotFoundError:
        print(f"Error: Text file '{txt_file_path}' not found")
        return {}
    except Exception as e:
        print(f"Error reading text file: {e}")
        return {}
    
    return games_data

def convert_txt_to_json(txt_file_path, games_directory, output_json_path):
    """
    Main function to convert TXT to JSON
    """
    print(f"Converting {txt_file_path} to {output_json_path}")
    print(f"Games directory: {games_directory}")
    print("-" * 50)
    
    # Parse the text file
    games_data = parse_txt_file(txt_file_path, games_directory)
    
    if not games_data:
        print("No games found or error occurred.")
        return False
    
    # Save to JSON file
    try:
        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(games_data, json_file, indent=4, ensure_ascii=False)
        
        print("-" * 50)
        print(f"Successfully created: {output_json_path}")
        print(f"Total consoles: {len(games_data)}")
        for console, games in games_data.items():
            print(f"  {console}: {len(games)} games")
        
        return True
    
    except Exception as e:
        print(f"Error writing JSON file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert TXT game list to JSON format')
    parser.add_argument('txt_file', help='Path to the input text file')
    parser.add_argument('games_dir', help='Path to the directory containing game files')
    parser.add_argument('-o', '--output', default='games.json', 
                       help='Output JSON file path (default: games.json)')
    
    args = parser.parse_args()
    
    # Convert the files
    success = convert_txt_to_json(args.txt_file, args.games_dir, args.output)
    
    if success:
        print("\nConversion completed successfully!")
    else:
        print("\nConversion failed!")
        return 1
    
    return 0

# Alternative: Simple function for direct use
def simple_convert(txt_file, games_dir, output_file="games.json"):
    """Simple one-function conversion without command line arguments"""
    return convert_txt_to_json(txt_file, games_dir, output_file)

if __name__ == "__main__":
    exit(main())