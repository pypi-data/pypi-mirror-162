





if __name__ == '__main__':
    from characters import *
    from races import *
    from competences import *
    elf = Race('elf')
    dworf = Race('dworf')
    test = Character([('force','30+1d10',100),('int','4d5',100)],elf)
    test.up('force')
    c = Competence('swim','pass a river',[elf,dworf])
    test.add_competence(c)
    print(test.test('force'))
    print(test)
