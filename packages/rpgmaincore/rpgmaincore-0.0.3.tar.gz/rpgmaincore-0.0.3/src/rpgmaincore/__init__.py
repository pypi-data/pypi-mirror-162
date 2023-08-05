from characters import *
from races import *





if __name__ == '__main__':
    test = Character([('force','30+1d10',100),('int','4d5',100)],Race('elf'))
    test.up('force')
    print(test.attributes)
    print(test.race)
    print(test.test('force'))
