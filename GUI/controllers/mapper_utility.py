import os
import sys

# ### CHANGE: Simplified pathing logic
# Assume map.txt is in the project root, where main.py is run from.
# This makes the path consistent regardless of the working directory.
project_root = os.path.dirname(os.path.abspath(sys.argv[0]))
MAP_FILE = os.path.join(project_root, "map.txt")

class GamepadMapperUtility:
    """
    Utility class to read, modify, and write the custom map.txt file.
    """
    def __init__(self, file_path=MAP_FILE):
        self.file_path = file_path
        self.mappings_data = {}
        self.comments_data = {} # ### CHANGE: Use dict for easier lookup
        self.line_order = []
        self._comment_counter = 0
        print(f"Mapper Utility initialized. Using map.txt at: {self.file_path}")

    def _parse_line(self, line: str):
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        if '=' in line:
            parts = line.split('=', 1)
            map_key = parts[0].strip()
            key_code = parts[1].split('#')[0].strip()
            if map_key and key_code:
                if map_key.isdigit() or ('_' in map_key and map_key.split('_')[0].isdigit()):
                    return map_key, key_code
        return None

    def read_mappings(self):
        if not os.path.exists(self.file_path):
            print(f"Warning: Mapping file not found at {self.file_path}. Creating a dummy file.")
            try:
                with open(self.file_path, 'w') as f:
                    f.write("# Default Gamepad Mappings\n")
                    f.write("0=KEY_X # Cross\n")
                    f.write("1_-1=KEY_UP # L-Stick UP\n")
            except Exception as e:
                print(f"Could not create map.txt: {e}")
                return False

        self.mappings_data.clear()
        self.comments_data.clear()
        self.line_order.clear()
        self._comment_counter = 0

        with open(self.file_path, 'r') as f:
            for line in f:
                map_result = self._parse_line(line)
                if map_result:
                    map_key, key_code = map_result
                    self.mappings_data[map_key] = key_code
                    self.line_order.append(('mapping', map_key))
                else:
                    comment_key = f"c{self._comment_counter}"
                    self.comments_data[comment_key] = line.rstrip('\n')
                    self.line_order.append(('comment', comment_key))
                    self._comment_counter += 1
        return True

    def update_mapping(self, map_key: str, new_key_code: str):
        if map_key in self.mappings_data:
            self.mappings_data[map_key] = new_key_code.strip().upper()
            return True
        else:
            print(f"Error: Map key '{map_key}' not found.")
            return False

    def write_mappings(self):
        try:
            with open(self.file_path, 'w') as f:
                for line_type, key in self.line_order:
                    if line_type == 'mapping':
                        line = f"{key}={self.mappings_data[key]}\n"
                        f.write(line)
                    elif line_type == 'comment':
                        line = self.comments_data[key]
                        f.write(line + '\n')
            print(f"Successfully wrote mappings to {self.file_path}")
            return True
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False

    def get_all_mappings(self):
        return self.mappings_data