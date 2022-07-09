import os
from tes_reader import ElderScrollsFileReader

game_folder = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Skyrim Special Edition\\'

game_file_path = os.path.join(game_folder, 'Data', 'Skyrim.esm')

with ElderScrollsFileReader(game_file_path) as elder_scrolls_file:
    book_count = len(elder_scrolls_file['BOOK'])
    print(f"Skyrim.esm has {book_count} books in it.")
