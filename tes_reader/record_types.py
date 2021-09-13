import struct
from . import Record, debug_record_attribute

class NPC(Record):
    def __init__(self, record):
        self._pointer = record._pointer
        self._header = record._header
        self._content = record.content

    @property
    def race_id(self):
        try:
            return hex(int.from_bytes(self['RNAM'], 'little', signed=False))
        except TypeError:
            return None

    @property
    @debug_record_attribute
    def is_female(self):
        return self._get_bit(self['ACBS'], 0)

    @property
    @debug_record_attribute
    def is_essential(self):
        return self._get_bit(self['ACBS'], 1)

    @property
    def is_preset(self):
        return self._get_bit(self['ACBS'], 2)

    @property
    def respawns(self):
        return self._get_bit(self['ACBS'], 3)

    @property
    def auto_calculate_stats(self):
        return self._get_bit(self['ACBS'], 4)

    @property
    def is_unique(self):
        return self._get_bit(self['ACBS'], 5)

    @property
    def is_protected(self):
        return self._get_bit(self['ACBS'], 11)

    @property
    def is_summonable(self):
        return self._get_bit(self['ACBS'], 14)

    @property
    def has_opposite_gender_animations(self):
        return self._get_bit(self['ACBS'], 19)

    @property
    def is_ghost(self):
        return self._get_bit(self['ACBS'], 29)

    @property
    def is_invulnerable(self):
        return self._get_bit(self['ACBS'], 31)


class Book(Record):
    def __init__(self, record):
        self._pointer = record._pointer
        self._header = record._header
        self._content = record.content

class Race(Record):
    def __init__(self, record):
        self._pointer = record._pointer
        self._header = record._header
        self._content = record.content

    @property
    def male_height(self):
        return struct.unpack('f', self['DATA'][16:20])[0]

    @property
    def female_height(self):
        return struct.unpack('f', self['DATA'][20:24])[0]

    @property
    def male_weight(self):
        return struct.unpack('f', self['DATA'][24:28])[0]

    @property
    def female_weight(self):
        return struct.unpack('f', self['DATA'][28:32])[0]

    @property
    def is_playable(self):
        return self._get_bit(self['DATA'][32:36], 0)