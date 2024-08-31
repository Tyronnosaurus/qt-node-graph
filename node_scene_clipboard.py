class SceneClipboard():
    """ Stores serialized data about copied and cut elements """
    
    def __init__(self, scene):
        self.scene = scene

    def serializeSelected(self, delete=False):
        return {}

    def deserializeFromClipboard(self, data):
        print("deserializating from clipboard, data:", data)
