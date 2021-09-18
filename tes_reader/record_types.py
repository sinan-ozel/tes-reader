import struct
from . import Record, FormId, debug_record_attribute

class NPC(Record):
    """A class to represent NPC_ type records.

    These records contain information about non-player characters (NPCs)."""
    def __init__(self, record):
        self._pointer = record._pointer
        self._header = record._header
        self._content = record.content

    @property
    def class_id(self):
        for class_field in self['CNAM']:
            return FormId(class_field)

    @property
    def race_id(self):
        for race_field in self['RNAM']:
            return FormId(race_field)

    @property
    def acbs(self):
        for acbs_field in self['ACBS']:
            return acbs_field

    @property
    @debug_record_attribute
    def is_female(self):
        return self._get_bit(self.acbs, 0)

    @property
    @debug_record_attribute
    def is_essential(self):
        return self._get_bit(self.acbs, 1)

    @property
    def is_preset(self):
        return self._get_bit(self.acbs, 2)

    @property
    def respawns(self):
        return self._get_bit(self.acbs, 3)

    @property
    def auto_calculate_stats(self):
        return self._get_bit(self.acbs, 4)

    @property
    def is_unique(self):
        return self._get_bit(self.acbs, 5)

    @property
    def is_levelling_up_with_pc(self):
        return self._get_bit(self.acbs, 7)

    @property
    def is_protected(self):
        return self._get_bit(self.acbs, 11)

    @property
    def is_summonable(self):
        return self._get_bit(self.acbs, 14)

    @property
    def has_opposite_gender_animations(self):
        return self._get_bit(self.acbs, 19)

    @property
    def is_ghost(self):
        return self._get_bit(self.acbs, 29)

    @property
    def is_invulnerable(self):
        return self._get_bit(self.acbs, 31)

    @property
    def level(self):
        if self.is_levelling_up_with_pc:
            divider = 1000
        else:
            divider = 1
        return int.from_bytes(self.acbs[8:10], 'little', signed=False) / divider



class Book(Record):
    """A class to represent BOOK type records.

    These records contain information about books."""
    def __init__(self, record):
        self._pointer = record._pointer
        self._header = record._header
        self._content = record.content

class Race(Record):
    """A class to represent RACE type records.

    These records contain information about character races."""
    def __init__(self, record):
        self._pointer = record._pointer
        self._header = record._header
        self._content = record.content

    @property
    def data(self):
        for data_field in self['DATA']:
            return data_field

    @property
    def male_height(self):
        return struct.unpack('f', self.data[16:20])[0]

    @property
    def female_height(self):
        return struct.unpack('f', self.data[20:24])[0]

    @property
    def male_weight(self):
        return struct.unpack('f', self.data[24:28])[0]

    @property
    def female_weight(self):
        return struct.unpack('f', self.data[28:32])[0]

    @property
    def is_playable(self):
        return self._get_bit(self.data[32:36], 0)

class CharacterClass(Record):
    """A class to represent CLAS type records.

    These records contain information about character classes."""
    def __init__(self, record):
        self._pointer = record._pointer
        self._header = record._header
        self._content = record.content

