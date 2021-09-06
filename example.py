import os
from tes_reader import Reader
from tes_reader.record_types import NPC

game_folder = 'S:\\Steam\\steamapps\\common\\Skyrim Special Edition\\'

with Reader(os.path.join(game_folder, 'Data', 'Skyrim.esm')) as skyrim_main_file:

    # Print the types of record in file
    print(skyrim_main_file.record_types)
    # Output is expected to include BOOK, NPC_, etc...

    # Print the number of books in file:
    print(len(skyrim_main_file['BOOK']))

    # List all of the Form ID (a.k.a. Base ID) for the NPC Records:
    for npc_record in skyrim_main_file['NPC_']:
        print(npc_record.form_id)

    # Load the full data for all NPC_ records and print their technical gender:
    for npc_record in skyrim_main_file['NPC_']:
        skyrim_main_file.load_record_content(npc_record)
        npc = NPC(npc_record)
        print('Form ID:', npc.form_id,
              '\tEssential?', npc.is_essential,
              '\tTechnical Gender:', lambda x: {True: 'F', False: 'M', None: 'No Gender (Should have base)'}[npc.is_female],
              '\tEditor ID:', npc.editor_id)

    # Inpect book records:
    for book_record in skyrim_main_file['BOOK']:
        # What types of fields do book records include?
        skyrim_main_file.load_record_content(book_record)
        print(book_record.form_id, {field.name for field in book_record})
        # Output: {'CNAM', 'INTV', 'HEDR', 'GRUP'}

    # Inspect the GRUP record of the book form ID 0x1acc7
    form_id = 0x1acc7
    skyrim_main_file.load_record_content(form_id)  # You can load the record contents using the Form ID
    book_record = skyrim_main_file[form_id]  # You can access a record by its Form ID.
    print(book_record['GRUP'])  # Hexadecimal output with four-letter Record types.

