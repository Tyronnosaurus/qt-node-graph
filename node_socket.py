from node_graphics_socket import QDMGraphicsSocket
from collections import OrderedDict
from node_serializable import Serializable


LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4

DEBUG = False


class Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socket_type=1, multi_edges=True):
        super().__init__()

        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.is_multi_edges = multi_edges

        if DEBUG: print("Socket -- creating with", self.index, self.position, "for node", self.node)

        self.grSocket = QDMGraphicsSocket(self, self.socket_type)

        self.grSocket.setPos(*self.node.getSocketPosition(index, position))

        self.edges = []


    def __str__(self):
        return "<Socket %s %s..%s>" % ("ME" if self.is_multi_edges else "SE", hex(id(self))[2:5], hex(id(self))[-3:])


    def getSocketPosition(self):
        if DEBUG: print("  GSP: ", self.index, self.position, "node:", self.node)
        res = self.node.getSocketPosition(self.index, self.position)
        if DEBUG: print("  res", res)
        return res


    def addEdge(self, edge):
        self.edges.append(edge)
    

    def removeEdge(self, edge):
        if edge in self.edges: self.edges.remove(edge)
        else: print("!W:", "Socket::removeEdge", "wanna remove edge", edge, "from self.edges but it's not in the list!")


    def removeAllEdges(self):
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove()


    def serialize(self):
        """ Returns the socket's properties as a dict for easy serialization """
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('multi_edges', self.is_multi_edges),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])


    def deserialize(self, data, hashmap={}, restore_id=True):
        """ Given json-serialized data about the socket, deserialize it and load it """        
        self.is_multi_edges = data['multi_edges']
        if restore_id: self.id = data['id']
        hashmap[data['id']] = self

