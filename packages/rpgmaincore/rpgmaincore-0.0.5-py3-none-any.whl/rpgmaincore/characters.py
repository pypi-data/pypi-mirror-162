from random import randint

class Character:
    """class corresponding to all types of characters"""
    def __init__(self,attributes_list=[],race=None):
        """creation of the Character w/ its attributes
        attributes_list : list of attributes
            attribute : (name,generation_rule,max)

        """
        self.generate(attributes_list)
        self.race = race
        self.competences = []
    def generate(self,attributes_list):
        """
        generation of the attributes
        attributes_list : list of attributes
            attribute : (name,generation_rule,max)

        """
        self.attributes = {name:(self.generate_one(rule),max) for name,rule,max in attributes_list}

    def generate_one(self,rule):
        """
        generate one attribute with the rule
        """
        val = 0
        for e in rule.split('+'):
            if 'd' in e:
                n,d = e.split('d')
                val += sum([randint(0,int(d)) for x in range(int(n))])
            else:
                val+=int(e)
        return val

    def change(self,attribute,value):
        """
        change the value of one attribute
        """
        c,max = self.attributes[attribute]
        self.attributes[attribute] = value,max
    def up(self,attribute,value=1):
        """
        raise one attribute by the value (1 by default)
        """
        c,max = self.attributes[attribute]
        self.attributes[attribute] = c+value,max
    def down(self,attribute,value=1):
        """
        raise down one attribute by the value (1 by default)
        """
        c,max = self.attributes[attribute]
        self.attributes[attribute] = c-value,max
    def test(self,attribute,bonus=0):
        """
        make a test of one attribute with a bonus (can be negative)
        """
        c,max = self.attributes[attribute]
        return randint(0,max)<=c+bonus
    def __repr__(self):
        r = ''
        if self.race:
            r+=self.race.__repr__()+'\n'
        if self.attributes:
            r+='attributes : \n'
        for name,ratio in self.attributes.items():
            n,m = ratio
            r+= "\t{} : {}/{}\n".format(name,n,m)
        if self.competences:
            r+='competences : \n'
            for c in self.competences:
                r+='\t'+c.__repr__()+'\n'
        return r
    def add_competence(self,competence):
        """add a compretence if it corresponds to the race of the character"""
        if self.race == competence.race:
            self.competences.append(competence)
