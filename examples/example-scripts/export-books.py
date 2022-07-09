import os
from glob import glob
from tes_reader import ElderScrollsFileReader, BethesdaSoftwareArchiveReader
from tes_reader.record_types import Book
from argparse import ArgumentParser

def main(filepath):
    file_path_without_extension = os.path.splitext(filepath)[0]
    file_name_without_extension = os.path.basename(file_path_without_extension)
    books = {}
    with ElderScrollsFileReader(filepath) as elder_scrolls_file:
        for book_record in elder_scrolls_file['BOOK']:
            elder_scrolls_file.load_record_content(book_record)
            book = Book(book_record)
            books[book.editor_id] = list(book['DESC'])[0]
            print(book.editor_id, [full_name for full_name in book['FULL']], [text for text in book['DESC']])


    for bsa_file_path in glob(file_path_without_extension + '*.bsa'):
        with BethesdaSoftwareArchiveReader(bsa_file_path) as bsa_file:
            if 'Strings' in bsa_file:
                print(f"Found a strings folder in the archive {bsa_file_path}")
                if bsa_file.is_compressed_by_default:
                    print(f"File is compressed by default.")
                if bsa_file.are_file_names_embedded:
                    print(f"File names are embedded")
                language = 'English'
                strings_file_name = f'{file_name_without_extension}_{language}.dlstrings'
                if strings_file_name in bsa_file['Strings']:
                    print(f"Found the strings file for the language {language}: {strings_file_name}")
                    file_bytes = bsa_file['Strings', strings_file_name]
                    number_of_entries = int.from_bytes(file_bytes[0:4], 'little', signed=False)
                    entries = {}
                    print("Number of entries", number_of_entries)
                    print("Size of the string data", int.from_bytes(file_bytes[4:8], 'little', signed=False))
                    for i in range(number_of_entries):
                        entries[file_bytes[8 + i * 8:12 + i * 8]] = int.from_bytes(file_bytes[12 + i * 8:16 + i * 8], 'little', signed=False)
                    raw_data_block_start = 8 + (i + 1) * 8
                    # for book_editor_id, book_string_id in books.items():
                    #     if book_string_id != b'\x00' * 4:
                    #         print(book_editor_id, entries[book_string_id])
                    #         print(file_bytes[raw_data_block_start + entries[book_string_id]:raw_data_block_start + entries[book_string_id] + 12])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("filepath")
    namespace = parser.parse_args()

    main(**vars(namespace))