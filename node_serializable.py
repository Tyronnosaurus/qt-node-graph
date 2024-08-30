class Serializable():
    """ Class to be inherited by other classes that should be serializable and deserializable. """
    
    def __init__(self):
        self.id = id(self)

    def serialize(self):
        raise NotImplemented()

    def deserialize(self, data, hashmap={}):
        raise NotImplemented()
