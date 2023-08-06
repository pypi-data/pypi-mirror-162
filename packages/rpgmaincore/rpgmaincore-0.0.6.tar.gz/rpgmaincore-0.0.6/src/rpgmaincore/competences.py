

class Competence:
    """class for the competence objects"""
    def __init__(self,name,effect,races):
        """creation of the object with a name, a races associated [] if any race can use it and a summary of the effect"""
        self.races = races
        self.name = name
        self.effect = effect
    def __repr__(self):
        if self.races == []:
            races = 'any'
        else:
            races = ';'.join([race.__repr__() for race in self.races])
        return "for {} {} : {}".format(races,self.name,self.effect)
