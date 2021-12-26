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


class FormId:
    # TODO: Implement __index__
    # TODO: Implement __format__
    def __init__(self, byte):
        if not isinstance(byte, (bytes, str)):
            raise ValueError("Use a string or byte object to instantiate a Form ID.")
        if isinstance(byte, str):
            if byte[:2] != '0x':
                raise ValueError("When creating a Form ID with a string, use a hexadecimal value. For examle: FormId('0x13bab')")
            if len(byte) > 8:
                self._bytes = int(byte, 16).to_bytes(4, byteorder='little')
            else:
                self._bytes = int(byte, 16).to_bytes(3, byteorder='little')
        else:
            if not len(byte) <= 4:
                raise ValueError("Form IDs have to have the length 4 bytes or less.")
            self._bytes = byte

    def __getitem__(self, key):
        return self._bytes[key]

    def __int__(self):
        return int.from_bytes(self._bytes, 'little', signed=False)

    def __index__(self):
        return int.from_bytes(self._bytes, 'little', signed=False)

    def __hex__(self):
        return hex(int.from_bytes(self._bytes, 'little', signed=False))

    def __str__(self):
        return str(hex(int.from_bytes(self._bytes, 'little', signed=False)))

    def __len__(self):
        return len(self._bytes)

    def __eq__(self, other):
        if isinstance(other, FormId):
            return self._bytes == other._bytes

    @property
    def modindex(self) -> bytes:
        if len(self) == 4:
            return self._bytes[-1]

    @property
    def objectindex(self):
        if len(self) == 4:
            return FormId(self._bytes[:-1])
        else:
            return self


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
        return self._bytes.decode('utf-8').strip('\0')

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

    # TODO: Add functions for each data type: _get_int, _get_uint, _get_float

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
                    yield field._bytes

    def _parse_subrecords_in_group(self, group):
        starting_position = group.pointer + group.header_size
        ending_position = starting_position + group.size - group.header_size
        _pos = starting_position
        while _pos < ending_position:
            record_header = self.content[_pos:_pos + Record.header_size]
            record = Record(_pos, record_header)
            if record.type == 'GRUP':
                subgroup = Group(_pos, record_header)
                self._parse_subrecords_in_group(subgroup)
                _pos += subgroup.size
            else:
                self.file[int(record.form_id)] = record
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
            return FormId(self._header[12:16])

    @property
    def timestamp(self):
        # TODO: Add formatting based on the Wiki page. Different in Skyrim SE and LE.
        return int.from_bytes(self._header[16:18], 'little', signed=False)

    def set_content(self, content: bytes):
        if not self.is_compressed:
            assert len(content) == self.size
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
        for editor_id in self['EDID']:
            return editor_id.decode('utf-8').strip('\0')


class Reader:
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError
        self.file_path = file_path

    def _read_bytes(self, pos: int, length: int=1) -> bytes:
        self._file.seek(pos)
        return self._file.read(length)

    def _read_string(self, _pos):
        _bytes = self._read_bytes(_pos)
        while _bytes[-1] != 0:
            _pos += 1
            _bytes += self._read_bytes(_pos)

        try:
            return _bytes[:-1].decode('utf-8')
        except UnicodeDecodeError:
            return _bytes[:-1].decode('latin-1')


class ElderScrollsFileReader(Reader):
    """Parse a ESM/P/L file.

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
        super().__init__(file_path)
        self._file = open(self.file_path, 'rb')
        try:
            assert self._read_bytes(0, 4) == b'TES4'
        except AssertionError:
            raise RuntimeError('Incorrect file header - is this a TES4 file?')
        self._read_all_record_headers()
        self.load_record_content(self['TES4'][0])
        self.tes4record = self['TES4'][0]
        self.masters = []
        if self.tes4record['MAST'] is not None:
            for master in self.tes4record['MAST']:
                self.masters += [master.decode('utf-8').strip('\0')]
        # TODO: Add CNAM and SNAM - Author & Description.
        # TOOD: Add the ESL bit, record count, group count and version.

    def __enter__(self):
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
            return self.records[int(key.form_id)]
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
                self.records[int(record.form_id)] = record
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
                self.records[int(record.form_id)] = record
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



class BethesdaSoftwareArchiveReader(Reader):
    """Parse a v104/105 (Skyrim) BSA File."""

    file_record_length = 16

    class Folder:
        def __init__(self, folder_index, folder_name, folder_record):
            folder_hash = BethesdaSoftwareArchiveReader._calculate_hash(folder_name)
            if folder_hash != folder_record['hash']:
                raise ValueError(f'Folder name {folder_name} resolves to the hash {folder_hash}, '
                                 f'but the hash in the folder record is {folder_record["hash"]}')
            self.name = folder_name
            self.index = folder_index
            self._hash = folder_record['hash']
            self._file_count = folder_record['file_count']
            self._offset = folder_record['offset']

        def __len__(self):
            return self._file_count

        def __repr__(self):
            return {
                'hash': self._hash,
                'file_count': self._file_count,
                'offset': self._offset
            }

        def __int__(self):
            return self._hash

        def __str__(self):
            return self.name

        def __iter__(self):
            for file_name in self._file_names:
                yield file_name

        # TODO: __contains__
        # TODO: __getitem__

        @property
        def record(self):
            return {
                'hash': self._hash,
                'file_count': self._file_count,
                'offset': self._offset
            }

    def __enter__(self):
        self._file = open(self.file_path, 'rb')
        try:
            assert self._read_bytes(0, 4) == b'BSA\x00'
        except AssertionError:
            raise RuntimeError('Incorrect file header - is this a BSA file?')

        if self.version == 104:
            self.folder_record_length = 16
        elif self.version == 105:
            self.folder_record_length = 24
        else:
            raise RuntimeError(f'Unknown BSA file version: {self.version}')
        self._load_folder_records()
        self._load_folder_filenames()
        # TODO: Add __len__
        # TODO: Add __iter__ ?
        return self

    def __exit__(self, exception_type, exception_val, trace):
        self._file.close()

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step is not None:
                raise KeyError(f'{self.__class__.__name__} does not allow slicing '
                                'with a step. Use only one colon in slice, for example: [0:4]')
            return self._read_bytes(key.start, key.stop - key.start)
        elif isinstance(key, str):
            return self._get_folder(key)
        elif isinstance(key, int):
            return self._get_folder_by_hash(key)
        else:
            raise KeyError

    def __contains__(self, key):
        if isinstance(key, int):
            return key in self._folders
        elif isinstance(key, str):
            hash = self._calculate_hash(key)
            return hash in self._folders
            # TODO: Add files and full paths.
        else:
            raise NotImplementedError

    def _load_folder_records(self):
        self._folders = {}
        for idx in range(self.folder_count):
            folder_name = self._get_folder_name_by_index(idx)
            folder_record = self._get_folder_record_by_index(idx)
            self._folders[folder_record['hash']] = self.Folder(idx, folder_name, folder_record)

    def _load_folder_filenames(self):
        file_names = self._get_file_names()
        self._folder_filenames = {}
        i = 0
        for folder_hash in self._folders:
            self._folders[folder_hash]._file_names = []
            while len(self._folders[folder_hash]._file_names) < self._folders[folder_hash]._file_count:
                self._folders[folder_hash]._file_names += [file_names[i]]
                i += 1
        if i != len(file_names):
            raise RuntimeError(f"Following files are not in a folder: {file_names[i:]}")

    def _get_file_index(self, folder_name, file_name):
        folder_hash = self._calculate_hash(folder_name)
        try:
            return self._folders[folder_hash]._file_names.index(file_name.lower())
        except ValueError:
            return None

    def _read_file_by_name(self, folder_name, file_name):
        file_record = self._get_file_record_by_name(folder_name, file_name)
        file_offset = file_record['offset']
        file_size = file_record['size']
        print(self[file_offset - 12:file_offset], self[file_offset:file_offset + 12])
        if self.are_file_names_embedded:
            raise NotImplementedError
        if file_record['is_compressed']:
            raise NotImplementedError
        return self[file_offset:file_offset + file_size]


    @staticmethod
    def _get_bit(longword: bytes, bit: int):
        try:
            return bool(int.from_bytes(longword, 'little', signed=False) & 2 ** bit)
        except TypeError:
            if longword is None:
                return None

    def _get_folder_record_by_index(self, idx):
        _pos = self.offset + idx * self.folder_record_length
        _bytes = self[_pos:_pos + self.folder_record_length]
        _pos_for_offset = 16 if self.version >= 105 else 12
        return {
            'hash': int.from_bytes(_bytes[0:8], 'little', signed=False),
            'file_count': int.from_bytes(_bytes[8:12], 'little', signed=False),
            'offset': int.from_bytes(_bytes[_pos_for_offset:_pos_for_offset + 4], 'little', signed=False),
        }

    def _get_folder_name_by_index(self, idx):
        offset = self._get_folder_record_by_index(idx)['offset']
        return self._read_string(offset - self.total_file_name_length + 1)

    def _get_file_names(self):
        last_folder_index = self.folder_count - 1
        last_folder_offset = self._get_folder_record_by_index(last_folder_index)['offset']
        last_folder_file_count = self._get_folder_record_by_index(last_folder_index)['file_count']
        file_count = 0
        for idx in range(self.folder_count):
            file_count += self._get_folder_record_by_index(idx)['file_count']
        last_folder_name = self._read_string(last_folder_offset - self.total_file_name_length + 1)
        file_name_list_offset = last_folder_offset - self.total_file_name_length + 1 + len(last_folder_name) + 1 + last_folder_file_count * self.file_record_length
        file_names = []
        while len(file_names) < file_count:
            file_name = self._read_string(file_name_list_offset)
            file_name_list_offset += len(file_name) + 1
            file_names += [file_name]
        if len(file_names) != self.file_count:
            raise RuntimeError(f"File count in the header is {self.file_count} but the list of file names is {len(file_names)}")
        return file_names

    # def _get_files_in_folder_by_index(self, folder_idx):
    #     folder_record = self._get_folder_record_by_index(folder_idx)
    #     file_count = folder_record['file_count']
    #     for file_idx in range(file_count):
    #         yield self._read_file_record_by_index(folder_idx, file_idx)

    def _read_file_record_bytes(self, folder_idx):
        folder_offset = self._get_folder_record_by_index(folder_idx)['offset']
        folder_name = self._read_string(folder_offset - self.total_file_name_length + 1)
        file_count = self._get_folder_record_by_index(folder_idx)['file_count']
        file_offset = folder_offset - self.total_file_name_length + 1 + len(folder_name) + 1 + file_count * self.file_record_length
        _bytes = self[file_offset:file_offset + self.file_record_length]
        return _bytes

    def _read_file_record_bytes_by_index(self, folder_idx, file_idx):
        folder_offset = self._get_folder_record_by_index(folder_idx)['offset']
        folder_name = self._read_string(folder_offset - self.total_file_name_length + 1)
        file_offset = folder_offset - self.total_file_name_length + 1 + len(folder_name) + 1 + file_idx * self.file_record_length
        _bytes = self[file_offset:file_offset + self.file_record_length]
        assert len(_bytes) == 16
        return _bytes

    def _read_file_record_by_index(self, folder_idx, file_idx):
        _bytes = self._read_file_record_bytes_by_index(folder_idx, file_idx)
        return {
            'hash': int.from_bytes(_bytes[0:8], 'little', signed=False),
            'size': int.from_bytes(_bytes[8:12], 'little', signed=False),
            'is_compressed': self._get_bit(_bytes[8:12], 29) ^ self.is_compressed_by_default,
            'offset': int.from_bytes(_bytes[12:16], 'little', signed=False),
        }

    def _get_file_record_by_name(self, folder_name, file_name):
        folder = self[folder_name]
        file_idx = self._get_file_index(folder_name, file_name)
        file_record = self._read_file_record_by_index(folder.index, file_idx)
        return file_record

    @property
    def folders(self):
        return list(self._folders.values())

    @property
    def folder_names(self):
        return [folder.name for folder in self._folders.values()]

    @staticmethod
    def _calculate_hash(path):
        """Returns tes4's two hash values for filename.

        Based on the code found at: https://en.uesp.net/wiki/Oblivion_Mod:Hash_Calculation

        In turn, based on TimeSlips code with cleanup and pythonization.
        """
        extensions = {'.kf': 0x80, '.nif': 0x8000, '.dds': 0x8080, '.wav': 0x80000000}
        path = path.lower()
        if any([path.endswith(ext) for ext in extensions]):
            ext = '.' + path.lower().split('.')[-1]
            base = path[:-len(ext)]
        else:
            ext = ''
            base = path

        chars = list(map(ord, base))
        hash1 = chars[-1] | (chars[-2] if len(chars) > 2 else 0) << 8 | len(chars) << 16 | chars[0] << 24
        if ext in extensions:
            hash1 |= extensions[ext]

        uint, hash2, hash3 = 0xffffffff, 0 , 0
        for char in chars[1:-2]:
            hash2 = ((hash2 * 0x1003F) + char ) & uint

        for char in ext:
            hash3 = ((hash3 * 0x1003F) + ord(char)) & uint

        hash2 = (hash2 + hash3) & uint

        return (hash2<<32) + hash1


    def _get_folder_by_hash(self, hash):
        return self._folders.get(hash)


    def _get_folder(self, folder_name):
        folder_name = folder_name.lower()
        folder_name = folder_name.strip('\\')
        hash = self._calculate_hash(folder_name)
        return self._get_folder_by_hash(hash)


    @property
    def version(self):
        return int.from_bytes(self[4:8], 'little', signed=False)

    @property
    def offset(self):
        return int.from_bytes(self[8:12], 'little', signed=False)

    @property
    def folder_count(self):
        return int.from_bytes(self[16:20], 'little', signed=False)

    @property
    def file_count(self):
        return int.from_bytes(self[20:24], 'little', signed=False)

    @property
    def total_folder_name_length(self):
        return int.from_bytes(self[24:28], 'little', signed=False)

    @property
    def total_file_name_length(self):
        return int.from_bytes(self[28:32], 'little', signed=False)

    @property
    def has_folder_names(self):
        return self._get_bit(self[12:16], 0)

    @property
    def has_file_names(self):
        return self._get_bit(self[12:16], 1)

    @property
    def is_compressed_by_default(self):
        return self._get_bit(self[12:16], 2)

    @property
    def are_file_names_embedded(self):
        return self._get_bit(self[12:16], 8)

    @property
    def contains_meshes(self):
        return self._get_bit(self[30:32], 0)

    @property
    def contains_textures(self):
        return self._get_bit(self[30:32], 1)


