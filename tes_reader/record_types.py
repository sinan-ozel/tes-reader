from . import Record

class NPC(Record):
    def __init__(self, record):
        self._pointer = record._pointer
        self._header = record._header
        self._content = record.content

    @property
    def is_female(self):
        return self._get_bit(self['ACBS'], 0)

    @property
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
