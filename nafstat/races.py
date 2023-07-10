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
    Race(3, 'Dark Elves', 'DE'),
    Race(4, 'Humans', 'Hu'),
    Race(5, 'Dwarves', 'Dw'),
    Race(6, 'High Elves', 'HE'),
    Race(7, 'Goblins', 'Gb'),
    Race(8, 'Halflings', 'Hl'),
    Race(9, 'Chaos Dwarves', 'CD'),
    Race(10, 'Chaos', 'Ch'),
    Race(11, 'Undead', 'Un'),
    Race(12, 'Wood Elves', 'WE'),
    Race(13, 'Norse', 'No'),
    Race(14, 'Amazons', 'Az'),
    Race(15, 'Lizardmen', 'Lz'),
    Race(16, 'Nurgle\'s Rotters', 'Nu'),
    Race(17, 'Khemri', 'Ke'),
    Race(18, 'Necromantic', 'Ne'),
    Race(19, 'Elves', 'PE'),
    Race(20, 'Ogres', 'Og'),
    Race(21, 'Vampires', 'Va'),
    Race(22, 'Slann', 'Sl'),
    Race(23, 'Underworld', 'UW'),
    Race(24, 'Chaos Pact', 'CP'),
    Race(25, 'Khorne', 'Ko'),
    Race(26, 'Bretonnians', 'Br'),
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

