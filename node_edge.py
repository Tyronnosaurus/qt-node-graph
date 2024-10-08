from node_graphics_edge import QDMGraphicsEdgeDirect, QDMGraphicsEdgeBezier
from collections import OrderedDict
from node_serializable import Serializable


EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2

DEBUG = False


class Edge(Serializable):
    """ Line or curve that connects two sockets """
    
    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EDGE_TYPE_DIRECT):

        super().__init__()

        self.scene = scene

        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type

        self.scene.addEdge(self)


    def __str__(self):
        return "<Edge %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    
    @property
    def start_socket(self): return self._start_socket


    @start_socket.setter
    def start_socket(self, value):
        # If we were assigned to some socket before, delete us from the socket
        if (self._start_socket is not None):
            self._start_socket.removeEdge(self)

        # Assign new start socket
        self._start_socket = value

        # Add edge to the socket
        if (self.start_socket is not None):
            self.start_socket.addEdge(self)


    @property
    def end_socket(self): return self._end_socket


    @end_socket.setter
    def end_socket(self, value):
        # If we were assigned to some socket before, delete us from the socket
        if (self._end_socket is not None):
            self._end_socket.removeEdge(self)

        # Assign new end socket
        self._end_socket= value

        # Add edge to the socket
        if (self.end_socket is not None):
            self.end_socket.addEdge(self)


    @property
    def edge_type(self): return self._edge_type


    @edge_type.setter
    def edge_type(self, value):
        if hasattr(self, 'grEdge') and self.grEdge is not None:
            self.scene.grScene.removeItem(self.grEdge)

        self._edge_type = value
        if self.edge_type == EDGE_TYPE_DIRECT:
            self.grEdge = QDMGraphicsEdgeDirect(self)
        elif self.edge_type == EDGE_TYPE_BEZIER:
            self.grEdge = QDMGraphicsEdgeBezier(self)
        else:
            self.grEdge = QDMGraphicsEdgeBezier(self)

        self.scene.grScene.addItem(self.grEdge)

        if self.start_socket is not None:
            self.updatePositions()


    def updatePositions(self):
        
        source_pos = self.start_socket.getSocketPosition()
        source_pos[0] += self.start_socket.node.grNode.pos().x()
        source_pos[1] += self.start_socket.node.grNode.pos().y()
        self.grEdge.setSource(*source_pos)
        
        if (self.end_socket is not None):
            end_pos = self.end_socket.getSocketPosition()
            end_pos[0] += self.end_socket.node.grNode.pos().x()
            end_pos[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDestination(*end_pos)
        else:
            self.grEdge.setDestination(*source_pos)
        
        self.grEdge.update()


    def remove_from_sockets(self):
        self.end_socket = None
        self.start_socket = None


    def remove(self):
        if DEBUG: print("# Removing Edge", self)

        if DEBUG: print(" - remove edge from all sockets")
        self.remove_from_sockets()

        if DEBUG: print(" - remove grEdge")
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None

        if DEBUG: print(" - remove edge from scene")
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass
        
        if DEBUG: print(" - everything is done.")


    def serialize(self):
        """ Returns the edge's properties as a dict for easy serialization """
        return OrderedDict([
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.id),
            ('end', self.end_socket.id),
        ])


    def deserialize(self, data, hashmap={}, restore_id=True):
        """ Given json-serialized data about the edge, deserialize it and load it """
        if restore_id: self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']