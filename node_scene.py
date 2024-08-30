from node_graphics_scene import QDMGraphicsScene
import json
from collections import OrderedDict
from node_serializable import Serializable


class Scene(Serializable):
    """ Wrapper around QDMGraphicsScene """

    def __init__(self):
        super().__init__()

        self.nodes = []
        self.edges = []

        self.scene_width = 16000
        self.scene_height = 16000

        self.initUI()


    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)


    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        self.nodes.remove(node)

    def removeEdge(self, edge):
        self.edges.remove(edge)


    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write( json.dumps( self.serialize(), indent=4 ) )
        print("saving to", filename, "was successfull.")


    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            raw_data = file.read()
            data = json.loads(raw_data, encoding='utf-8')
            self.deserialize(data)


    def serialize(self):
        """ Returns the scene's properties as a dict for easy serialization """
        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', [node.serialize() for node in self.nodes]),
            ('edges', [edge.serialize() for edge in self.edges]),
        ])


    def deserialize(self, data, hashmap={}):
        print("deserializating data", data)
        return False
