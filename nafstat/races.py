from collections import namedtuple

Race=namedtuple("Race", "race_id race sh")
INDEX = (
    Race(0, 'All Races', '*'),
    Race(1, 'Orc', 'Or'),
    Race(2, 'Skaven', 'Sk'),
    Race(3, 'Dark Elves', 'DE'),
    Race(4, 'Humans', 'Hu'),
    Race(5, 'Dwarves', 'Dw'),
    Race(6, 'High Elves', 'HE'),
    Race(7, 'Goblins', 'Go'),
    Race(8, 'Halflings', 'Hl'),
    Race(9, 'Chaos Dwarves', 'CD'),
    Race(10, 'Chaos', 'Ch'),
    Race(11, 'Undead', 'Un'),
    Race(12, 'Wood Elves', 'WE'),
    Race(13, 'Norse', 'No'),
    Race(14, 'Amazons', 'Am'),
    Race(15, 'Lizardmen', 'Li'),
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
    Race(27, 'Multiple Races', 'XX'))