"""A module to read and parse TES (The Elder Scrolls) files.

Usage Example - Print Form IDs of all top-level NPC records in Skyrim.esm
    from tes_reader import Reader

    game_folder = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Skyrim Special Edition\\'

    with Reader(os.path.join(game_folder, 'Data', 'Skyrim.esm')) as skyrim_main_file:
        for npc in skyrim_main_file['NPC_']:
            print(npc.form_id)


Credits: This code is mainly written from the YouTube stream found at https://www.youtube.com/watch?v=w5TLMn5l0g0
and the explanation on the Wiki page: https://en.uesp.net/wiki/Skyrim_Mod:Mod_File_Format
"""
__version__ = '0.0.7'
__author__ = 'Sinan Ozel'

import re
import os
import zlib
import struct
from typing import Union, List

# TODO: There is a faster way to check if all four characters are uppercase ASCII: AND against one particular bit.
type_regular_expression = re.compile('[A-Z_0-9]{4}')
def is_type(alleged_type_string: str):
    return type_regular_expression.match(alleged_type_string)

def debug_record_attribute(func):
    """Decorator to print debugging information about the record."""
    def func_with_debug(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except Exception:
            print(self.type)
            print(self._content)
            print([field.name for field in self.fields])
            raise

        return result
    return func_with_debug


class Field:
    header_size = 6

    def __init__(self, content: bytes):
        assert len(content) >= self.header_size
        self._pos = 0
        self.name = self.get_name_from_content(content)
        self.size = self.get_size_from_content(content)
        self._bytes = content[self.header_size:self.header_size + self.size]

    @staticmethod
    def get_name_from_content(content: bytes):
        return content[0:4].decode('utf-8')

    @staticmethod
    def get_size_from_content(content: bytes):
        return int.from_bytes(content[4:6], 'little', signed=False)

    def __str__(self):
        return self._bytes.decode('utf-8')

    def __int__(self):
        return int.from_bytes(self._bytes, 'little', signed=False)

    def __float__(self, offset=0):
        return struct.unpack('f', self._bytes)[0 + offset]

    def __len__(self):
        return self.header_size + self.size

class Group:
    header_size = 24

    # See https://en.uesp.net/wiki/Skyrim_Mod:Mod_File_Format for the full list.
    # TODO: Add the remaining.
    group_types = [
        'Top',
        'World Children',
        'Interior Cell Block',
        'Interior Cell Sub-Block',
    ]

    def __init__(self, pointer: int, header):
        cls = self.__class__
        if type(header) != bytes or len(header) != 24:
            raise ValueError(f'To initialize a {cls.__name__} object, pass a {self.header_size}-byte value read from the position in the file.')
        self._pointer = pointer
        self._header = header
        if self.type != 'GRUP':
            raise TypeError(f'Not a GRUP. Type is: {self.type}')

    @property
    def size(self):
        return int.from_bytes(self._header[4:8], 'little', signed=False)

    @property
    def type(self):
        try:
            return self._header[0:4].decode('utf-8')
        except UnicodeDecodeError:
            return self._header[0:4].decode('latin-1').strip('\0')

    @property
    def group_type(self):
        return int.from_bytes(self._header[12:16], 'little', signed=False)

    @property
    def label(self):
        if self.group_type == 0:
            try:
                return self._header[8:12].decode('utf-8')
            except UnicodeDecodeError:
                return self._header[8:12].decode('latin-1').strip('\0')
        elif self.group_type in [1, 6, 7, 8, 9]:
            return int.from_bytes(self._header[8:12], 'little', signed=False) # Form Id.

    @property
    def version(self):
        return int.from_bytes(self.buffer[18:20], 'little', signed=False)

    @property
    def pointer(self):
        return self._pointer




class Record:
    header_size = 24

    def __init__(self, pointer: int, header: bytes):
        cls = self.__class__
        if type(header) != bytes or len(header) != 24:
            raise ValueError(f'To initialize a {cls.__name__} object, pass a {self.header_size}-byte value read from the position in the file.')
        self._pointer = pointer
        self._header = header

    def __len__(self):
        return self.header_size + self.size

    def __repr__(self):
        return f'Record(pointer={self._pointer}, header={self._header}'

    def __str__(self):
        return f'{self.type} record at position {self._pointer}, with size {self.size}, Form ID: {self.form_id}'

    def __setattr__(self, name, value):
        if name == 'content':
            self.set_content(value)
        else:
            self.__dict__[name] = value

    def __getitem__(self, key: Union[str, slice]) -> bytes:
        if isinstance(key, slice):
            return self.content[key]
        if isinstance(key, str):
            for field in self:
                if field.name == key:
                    return field._bytes

    def _parse_subrecords_in_group(self, group):
        starting_position = group.pointer + group.header_size
        ending_position = starting_position + group.size - group.header_size
        _pos = starting_position
        print("Parsing subrecords.")
        while _pos < ending_position:
            record_header = self.content[_pos:_pos + Record.header_size]
            record = Record(_pos, record_header)
            if record.type == 'GRUP':
                subgroup = Group(_pos, record_header)
                self._parse_subrecords_in_group(subgroup)
                _pos += subgroup.size
            else:
                self.fie[int(record.form_id, 16)] = record
                if not is_type(record.type):
                    print(f'Weird record type: {record.type}')
                    break
                _pos += record.header_size + record.size

        if _pos != ending_position:
            raise RuntimeError(f"Record Group of size {group.size} starting at {starting_position}, ending at {starting_position + group.size}, ended unexpectedly at position: {_pos}")

    def _parse_contents(self, starting_position=0, ending_position=None):
        self._field_pointers = []
        self._field_sizes = []
        self.subrecords = {}
        if ending_position is None:
            ending_position = self.size
        _pos = starting_position
        self.fields = []
        while _pos < ending_position:
            field = Field(self.content[_pos:])
            if field.name == 'GRUP':
                group_header = self.content[_pos:_pos + Group.header_size]
                group = Group(_pos, group_header)
                self._parse_subrecords_in_group(group)
                _pos += group.size
            else:
                self._field_pointers += [_pos]
                self._field_sizes += [Field.header_size + Field.get_size_from_content(self.content[_pos:_pos + 6])]
                self.fields += [field]
                _pos += field.header_size + field.size

    def __iter__(self):
        if not hasattr(self, '_field_pointers'):
            self._parse_contents()
        for i, _pos in enumerate(self._field_pointers):
            field_size = self._field_sizes[i]
            yield Field(self.content[_pos:_pos + field_size])

    @property
    def field_types(self):
        return {field.name for field in self}

    @property
    def type(self):
        try:
            return self._header[0:4].decode('utf-8')
        except UnicodeDecodeError:
            return self._header[0:4].decode('latin-1').strip('\0')

    @property
    def is_compressed(self):
        if self.type == 'GRUP':
            return False
        return self._get_flag(18)

    @property
    def is_esm(self):
        return self._get_flag(0)

    def _get_flag(self, bit):
        return self._get_bit(self._header[8:12], bit)
        # return bool(int.from_bytes(self._header[8:12], 'little', signed=False) & 2 ** bit)

    @staticmethod
    def _get_bit(longword: bytes, bit: int):
        try:
            return bool(int.from_bytes(longword, 'little', signed=False) & 2 ** bit)
        except TypeError:
            if longword is None:
                return None

    @property
    def size(self):
        return int.from_bytes(self._header[4:8], 'little', signed=False)

    @property
    def label(self):
        if self.type == 'GRUP':
            return int.from_bytes(self._header[8:12], 'little', signed=False)

    @property
    def version(self):
        if self.type == 'GRUP':
            return int.from_bytes(self.buffer[18:20], 'little', signed=False)
        else:
            return int.from_bytes(self.buffer[20:22], 'little', signed=False)

    @property
    def form_id(self):
        if self.type != 'GRUP':
            return hex(int.from_bytes(self._header[12:16], 'little', signed=False))

    @property
    def timestamp(self):
        # TODO: Add formatting based on the Wiki page. Different in Skyrim SE and LE.
        return int.from_bytes(self._header[16:18], 'little', signed=False)

    def set_content(self, content: bytes):
        # if hasattr(self, '_content'):
        #     raise RuntimeError(f'Cannot run set_content more than once on the same {self.__class__.__name__}.')
        if not self.is_compressed:
            assert len(content) == self.size
        # print(content[0:4].decode('utf-8'))
        # if re.match("[A-Z0-9_]{4}", content[0:4].decode('utf-8')):
        #     raise ValueError('Content should start with four uppercase letters or underscore.')
        self._content = content

    def get_content(self):
        try:
            return self._content
        except AttributeError:
            raise AttributeError('Record contents not loaded. Call set_content to set them.')

    @property
    def content(self):
        return self.get_content()

    @property
    def editor_id(self):
        return self['EDID'].decode('utf-8').strip('\0')


class Reader:
    """Parse a TES4 file.

    Usage examples:

    from elder_scrolls import Reader

    with Reader(os.path.join(game_folder, 'Data', 'Skyrim.esm')) as skyrim_main_file:
        print(len(skyrim_main_file['BOOK']))  # print the number of BOOK records.

        print(skyrim_main_file.record_types)  # print types of records in file.

        for npc in skyrim_main_file['NPC_']:
            print(npc.form_id)  # Print form IDs of all NPCs.

        print(skyrim_main_file[0x1033ee])  # Return the record with the form ID 0x1033ee
    """

    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError
        self.file_path = file_path

    def __enter__(self):
        self._file = open(self.file_path, 'rb')
        try:
            assert self._read_bytes(0, 4) == b'TES4'
        except AssertionError:
            raise RuntimeError('Incorrect file header - is this a TES4 file?')
        self._read_all_record_headers()
        return self

    def __exit__(self, exception_type, exception_val, trace):
        self._file.close()

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step is not None:
                raise KeyError(f'{self.__class__.__name__} does not allow slicing '
                                'with a step. Use only one colon in slice, for example: [0:4]')
            return self._read_bytes(key.start, key.stop - key.start)
        elif isinstance(key, int):
            return self.records[key]
        elif isinstance(key, Record):
            return self.records[int(key.form_id, 16)]
        elif isinstance(key, str):
            if len(key) == 4:
                return [record for record in self.records.values() if record.type == key]
            elif key[:2] == '0x':
                return self.records[int(key, 16)]
        else:
            raise KeyError

    def __iter__(self):
        return iter(self.records.values())

    def __len__(self):
        return len(self.records)

    def __contains__(self, val):
        return val in self.records or val in self.record_types

    @property
    def pos(self):
        return self._file.tell()

    @property
    def record_types(self) -> set:
        return {record.type for record in self.records.values()}

    def _reset(self):
        self._file.seek(0)

    def _read_bytes(self, pos: int, length: int) -> bytes:
        self._file.seek(pos)
        return self._file.read(length)

    def _read_record_header(self, pos):
        return self._read_bytes(pos, 24)

    def _read_record_headers_in_group(self, starting_position, size):
        _pos = starting_position
        ending_position = starting_position + size
        while _pos < ending_position:
            record_header = self._read_record_header(_pos)
            record = Record(_pos, record_header)
            if record.type == 'GRUP':
                group = Group(_pos, record_header)
                self._read_record_headers_in_group(_pos + group.header_size, group.size - group.header_size)
                _pos += group.size
            else:
                self.records[int(record.form_id, 16)] = record
                if not is_type(record.type):
                    print(f'Weird record type: {record.type}')
                    break
                _pos += record.header_size + record.size

        if _pos != ending_position:
            raise RuntimeError(f"Record Group of size {group.size} starting at {starting_position}, ending at {starting_position + group.size}, ended unexpectedly at position: {_pos}")


    def _read_all_record_headers(self):
        self.records = {}
        record_position = 0
        while True:
            record_header = self._read_record_header(record_position)
            try:
                record = Record(record_position, record_header)
            except ValueError:
                if len(record_header) != 0:
                    raise RuntimeWarning(f"File ended unexpectedly at position: {record_position}")
                break
            if record.type == 'GRUP':
                group = Group(record_position, record_header)
                self._read_record_headers_in_group(record_position + group.header_size, group.size - group.header_size)
                record_position += group.size
            else:
                self.records[int(record.form_id, 16)] = record
                record_position += record.header_size + record.size

    def get_record_content(self, record: Union[str, int, Record]) -> bytes:
        try:
            return self[record].content
        except AttributeError:
            self.load_record_content(record)
            return self[record].content

    def load_record_content(self, record: Union[str, int, Record]):
        if self[record].is_compressed:
            content = self._read_bytes(self[record]._pointer + self[record].header_size + 4, self[record].size)
            content = zlib.decompress(content, zlib.MAX_WBITS)
            record.set_content(content)
        else:
            content = self._read_bytes(self[record]._pointer + self[record].header_size, self[record].size)
        self[record].content = content

