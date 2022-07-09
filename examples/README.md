# How to Use the Examples

You can run the examples in two different ways:

1. Without a container: Choose this if you have Python installed, and you are not familiar with Docker containers.
2. With a container: Choose this if you have Docker installed, and you prefer keeping your environment clean.


Each script has its help file, for instance, you can run `export_books.py --help`

## Running the examples without a container

1. Install Python if you don't have it.
2. Install TES Reader: `pip install tes-reader`
TODO: Add the rest

## Running the examples inside a container

1. Make sure that Docker is installed.
2. Run the following command: `$env:SKYRIM_PATH="<Your Skyrim Path>"; docker-compose build`. (You need to run this only once. If the path is incorrect, or if it changes, just re-run, it will overwrite.) Example: `$env:SKYRIM_PATH="C:\\Program Files (x86)\\Steam\\steamapps\\common\\Skyrim Special Edition"; docker-compose build`
2. Run the following command: `docker-compose run tes-reader-examples`.
3. Now run any one of the Python scripts.

The container is slightly over 100 MBs, as I am using a slim version of Python.