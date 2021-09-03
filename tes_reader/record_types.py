from . import Record

class Group(Record):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def label(self):
        return int.from_bytes(self._header[8:12], 'little', signed=False)
    
    @property
    def version(self):
        return int.from_bytes(self.buffer[18:20], 'little', signed=False)

class NPC(Record):
    def __init__(self, record):
        self._pointer = record._pointer
        self._header = record._header
        self.content = record._content

    @property
    def is_female(self):
        return self._get_bit(self['ACBS'], 0)

