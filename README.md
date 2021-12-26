# The Elder Scrolls Files Reader
A reader for The Elder Scrolls files.

## Minimal Example - Print the Number of Books
```
import os
from tes_reader import ElderScrollsFileReader

game_folder = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Skyrim Special Edition\\'

game_file_path = os.path.join(game_folder, 'Data', 'Skyrim.esm')

with ElderScrollsFileReader(game_file_path) as elder_scrolls_file:
    book_count = len(elder_scrolls_file['BOOK'])
    print(f"Skyrim.esm has {book_count} books in it.")
```

See [example.py](https://github.com/sinan-ozel/tes-reader/blob/main/example.py) for more examples.

## Installation

```
pip install tes-reader
```
## Requirements
* Python 3.5+
* pip (Package manager for Python)
* Windows
* An Elder Scrolls Game - for example, Skyrim.

## Support and Future Development

I have some more examples of use, I plan to add these to the git repo.

I also plan to expand the in-code documentation and add a short manual.


## Development and Testing

Clone from github using `git clone git@github.com:sinan-ozel/tes-reader.git`

Install the requirements for development using the command `pip install -r requirements/dev.txt`. I personally prefer
using a virtualenv to keep modules organized.

To run the tests, you will need computer with Skyrim installed. Go into the `tests` folder. Set the configuration in the `test.ini` file to point to the Skyrim's executable folder (not the data folder). Finally, run the command `py.test -v`, while inside the `tests` folder.
