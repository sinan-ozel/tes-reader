# How to Use the Examples

You can run the examples in two different ways:

1. Without a container: Choose this if you have Python installed, and you are not familiar with Docker containers.
2. With a container: Choose this if you have Docker installed, and you prefer keeping your environment clean.


Each script has its help file, for instance, you can run `export_books.py --help`

## Running the examples without a container

1. Install Python if you don't have it.
2. Install TES Reader: `pip install tes-reader`
3. Go into the folder `examples/example-scripts`
4. In this folder, run the scripts as if you would run a usual Python script, i.e. `python minimal-example.py` or `python3 minimal-example.py`. 

Sample output from Git Bash:
```
MINGW64 /d/GitHub/tes-reader/examples/example-scripts (add-examples)
$ python minimal-example.py
Skyrim.esm has 821 books in it.
```

The following script will output the book contents in any mod. It doesn't really "export" them, just outputs on the screen.
```
MINGW64 /d/GitHub/tes-reader/examples/example-scripts (add-examples)
$ python export-books.py "C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition\Data\Book Covers Skyrim.esp"
```

## Running the examples inside a container

1. Make sure that Docker is installed.
2. Run the following command: `$env:SKYRIM_PATH="<Your Skyrim Path>"; docker-compose build`. (You need to run this only once. If the path is incorrect, or if it changes, just re-run, it will overwrite.) Example: `$env:SKYRIM_PATH="C:\\Program Files (x86)\\Steam\\steamapps\\common\\Skyrim Special Edition"; docker-compose build`
2. Run the following command: `docker-compose run tes-reader-examples`.
3. Now run any one of the Python scripts.

The container is slightly over 100 MBs, as I am using a slim version of Python.