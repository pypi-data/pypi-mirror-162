

class Race:
    """class for the race object with all infos about each race"""
    def __init__(self,name):
        """creation of the race with its name"""
        self.name = name

    def __repr__(self):
        return self.name
