

class Competence:
    """class for the competence objects"""
    def __init__(self,name,effect,race):
        """creation of the object with a name, a race associated and a summary of the effect"""
        self.race = race
        self.name = name
        self.effect = effect
    def __repr__(self):
        return "for {} {} : {}".format(self.race.__repr__(),self.name,self.effect)
