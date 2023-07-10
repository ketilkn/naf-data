from collections import namedtuple


class ImmutableDict(dict):
    def __setitem__(self, key, value):
        raise TypeError("%r object does not support item assignment" % type(self).__name__)

    def __delitem__(self, key):
        raise TypeError("%r object does not support item deletion" % type(self).__name__)

    def __getattribute__(self, attribute):
        if attribute in ('clear', 'update', 'pop', 'popitem', 'setdefault'):
            raise AttributeError("%r object has no attribute %r" % (type(self).__name__, attribute))
        return dict.__getattribute__(self, attribute)

    def __hash__(self):
        return hash(tuple(sorted(self.iteritems())))

    def fromkeys(self, S, v):
        return type(self)(dict(self).fromkeys(S, v))


Race = namedtuple("Race", "race_id race sh")

INDEX = (
    Race(0, 'All Races', '*'),
    Race(1, 'Orc', 'Or'),
    Race(2, 'Skaven', 'Sk'),
    Race(3, 'Dark Elf', 'DE'),
    Race(4, 'Human', 'Hu'),
    Race(5, 'Dwarf', 'Dw'),
    Race(6, 'High Elf', 'HE'),
    Race(7, 'Goblin', 'Gb'),
    Race(8, 'Halfling', 'Hl'),
    Race(9, 'Chaos Dwarf', 'CD'),
    Race(10, 'Chaos Chosen', 'Ch'),
    Race(11, 'Shambling Undead', 'Un'),
    Race(12, 'Wood Elf', 'WE'),
    Race(13, 'Norse', 'No'),
    Race(14, 'Amazon', 'Az'),
    Race(15, 'Lizardmen', 'Lz'),
    Race(16, 'Nurgle', 'Nu'),
    Race(17, 'Tomb Kings', 'Ke'),
    Race(18, 'Necromantic Horror', 'Ne'),
    Race(19, 'Elf Union', 'PE'),
    Race(20, 'Ogre', 'Og'),
    Race(21, 'Vampires', 'Va'),
    Race(22, 'Slann', 'Sl'),
    Race(23, 'Underworld Denizens', 'UW'),
    Race(24, 'Chaos Renegade', 'CP'),
    Race(25, 'Daemons of Khorne', 'Ko'),
    Race(26, 'Bretonnian', 'Br'),
    Race(27, 'Draft', 'Df'),
    Race(28, 'Old World Alliance', 'Ow'),
    Race(29, 'Snotling', 'Sn'),
    Race(30, 'Black orc', 'Bo'),
    Race(31, 'Imperial Nobility', 'In'),
    Race(99, 'Multiple Races', 'XX'))


def race_dict():
    return ImmutableDict(zip([r.race for r in INDEX], INDEX))


Races = namedtuple("Races", 'by_id by_race')

RACES = Races(INDEX, race_dict())

