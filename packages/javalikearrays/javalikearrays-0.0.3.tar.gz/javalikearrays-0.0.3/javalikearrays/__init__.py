class BArray():

    # RootHandler
    class RootHandler():
        roots = None
        def __init__(self):
            self.roots = [
                ["SORTED" , False],
                ["TYPE", "None"],
                ["LENGTH", 0],
                ["FORCE_LENGTH", True]
                ["FORCE_TYPE", True]
                # Only Enable for Experimental Behavior, can cause unsafe activity
                ["EXPERIMENTAL", False]
                # Only Enable for Experimental Behavior, can cause unsafe activity
                ["MODE_UNSAFE", False]
            ]

    # RootObject
    class RootObject(RootHandler):

        def __init__(self):
            super().__init__()

        def setFlag(self, flag:str, flagValue):
            return None
        
        def root(self, root:str):
            length = len(self.roots)
            for i in range(length-1):
                if self.roots[i][0] == root:
                    return self.roots[i][1]

    _holding = None
    # Makes the Root Object Accessible
    rootObject = RootObject()

    _refference = {
        'int':0,
        'str':'',
        'float':0.0,
        'boolean':False,
        'complex':0 + 0j
    }

    def __init__(self, type: str, len: int):
        self.rootObject.roots[1][1] = type
        self.rootObject.roots[2][1] = len
        self.make()
    
    def make(self):
        if self.rootObject.roots[1][1] in self._refference:
            self._holding = [self._refference.get(self.rootObject.roots[1][1])] * self.rootObject.roots[2][1]
        else:
            print("Type Cannot Exist in BArray, Destrcting Object")
            del self
            del rootObject

    def __len__(self):
        return self.rootObject.roots[2][1]
    
    def __repr__(self):
        return self._holding
    
    def __str__(self):
        return str(self.__repr__())


