# The Elder Scrolls Files Reader
A reader for The Elder Scrolls files.

## Minimal Example - Print the Number of Books
```
from tes_reader import Reader

game_folder = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Skyrim Special Edition\\'

with Reader(os.path.join(game_folder, 'Data', 'Skyrim.esm')) as skyrim_main_file:
    print(len(skyrim_main_file['BOOK']))
```

See [example.py](https://github.com/sinan-ozel/tes-reader/blob/main/example.py) for more examples.

## Installation

```
pip install tes-reader
```
## Requirements
* Python 3.5
* pip (Package manager for Python)
* Windows
* An Elder Scrolls Game - for example, Skyrim.

## Development and Testing

In addition to the requirements above, you will need a github.com account, and the `pytest` package, installed with `pip install pytest`

Clone from github using `git clone git@github.com:sinan-ozel/tes-reader.git`

To run the tests, you will need computer with Skyrim installed. Go into the `tests` folder. Set the configuration in the `test.ini` file to point to the Skyrim's executable folder (not the data folder). Finally, run the command `pytest -v`, while inside the `tests` folder.
