from node_graphics_scene import QDMGraphicsScene
import json
from collections import OrderedDict
from node_serializable import Serializable
from node_node import Node
from node_edge import Edge
from node_scene_history import SceneHistory
from node_scene_clipboard import SceneClipboard


class Scene(Serializable):
    """ Wrapper around QDMGraphicsScene """

    def __init__(self):
        super().__init__()

        self.nodes = []
        self.edges = []

        self.scene_width = 16000
        self.scene_height = 16000

        self._has_been_modified = False
        self._has_been_modified_listeners = []

        self.initUI()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)


    @property
    def has_been_modified(self):
        return False
        # return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            self._has_been_modified = value

            # Call all registered listeners
            for callback in self._has_been_modified_listeners:
                callback()

        self._has_been_modified = value


    def addHasBeenModifiedListener(self, callback):
        self._has_been_modified_listeners.append(callback)


    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)


    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        if node in self.nodes: self.nodes.remove(node)
        else: print("!W:", "Scene::removeNode", "wanna remove node", node, "from self.nodes but it's not in the list!")

    def removeEdge(self, edge):
        if edge in self.edges: self.edges.remove(edge)
        else: print("!W:", "Scene::removeEdge", "wanna remove edge", edge, "from self.edges but it's not in the list!")


    def clear(self):
        """ Delete all nodes, one by one, with their remove() method so that they also delete any connected edge """
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False


    def saveToFile(self, filename):
        """ Save scene data in a json file """
        with open(filename, "w") as file:
            file.write( json.dumps( self.serialize(), indent=4 ) )
            print("Saving to", filename, "was successfull.")
            self.has_been_modified = False


    def loadFromFile(self, filename):
        """ Reads scene data stored in a json file, and deserializes it to recreate all the elements in the scene """
        with open(filename, "r") as file:
            raw_data = file.read()
            data = json.loads(raw_data)
            self.deserialize(data)
            self.has_been_modified = False


    def serialize(self):
        """ Returns the scene's properties as a dict for easy serialization """
        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', [node.serialize() for node in self.nodes]),
            ('edges', [edge.serialize() for edge in self.edges]),
        ])


    def deserialize(self, data, restore_id=True):
        """ Given json-serialized data about the scene and its contents, deserialize it and load it """
        print("Deserializing data")
        self.clear()
        hashmap = {}

        if restore_id: self.id = data['id']

        # Create nodes
        for node_data in data['nodes']:
            Node(self).deserialize(node_data, hashmap, restore_id)

        # Create edges
        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap, restore_id)