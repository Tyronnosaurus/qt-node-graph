from node_graphics_scene import QDMGraphicsScene
import json
from collections import OrderedDict
from node_serializable import Serializable
from node_node import Node
from node_edge import Edge


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


    def clear(self):
        """ Delete all nodes, one by one, with their remove() method so that they also delete any connected edge """
        while len(self.nodes) > 0:
            self.nodes[0].remove()


    def saveToFile(self, filename):
        """ Save scene data in a json file """
        with open(filename, "w") as file:
            file.write( json.dumps( self.serialize(), indent=4 ) )
        print("Saving to", filename, "was successfull.")


    def loadFromFile(self, filename):
        """ Reads scene data stored in a json file, and deserializes it to recreate all the elements in the scene """
        with open(filename, "r") as file:
            raw_data = file.read()
            data = json.loads(raw_data)
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


    def deserialize(self, data):
        """ Given json-serialized data about the scene and its contents, deserialize it and load it """
        print("Deserializing data")
        self.clear()
        hashmap = {}

        # Create nodes
        for node_data in data['nodes']:
            Node(self).deserialize(node_data, hashmap)

        # Create edges
        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap)