from node_graphics_node import QDMGraphicsNode
from node_content_widget import QDMNodeContentWidget
from node_socket import *
from collections import OrderedDict
from node_serializable import Serializable


DEBUG = False


class Node(Serializable):

    def __init__(self, scene, title="New node", inputs=[], outputs=[]):
            
        super().__init__()

        self._title = title
        self.scene = scene

        self.content = QDMNodeContentWidget(self)
        self.grNode = QDMGraphicsNode(self)

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        self.socket_spacing = 22

        # Create sockets for inputs and outputs
        self.inputs = []
        self.outputs = []

        counter = 0
        for item in inputs:
            socket = Socket(node=self, index=counter, position=LEFT_BOTTOM, socket_type=item)
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for item in outputs:
            socket = Socket(node=self, index=counter, position=RIGHT_TOP, socket_type=item)
            counter += 1
            self.outputs.append(socket)


    def __str__(self):
        return "<Node %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])


    @property
    def pos(self):
        return self.grNode.pos()  # QPointF
    
    def setPos(self, x, y):
        self.grNode.setPos(x, y)


    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title


    def getSocketPosition(self, index, position):
        x = 0 if (position in (LEFT_TOP, LEFT_BOTTOM)) else self.grNode.width

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # Start from bottom
            y = self.grNode.height - self.grNode.edge_size - self.grNode._padding - index * self.socket_spacing
        else:
            # Start from top
            y = self.grNode.title_height + self.grNode._padding + self.grNode.edge_size + index * self.socket_spacing

        return [x, y]


    def updateConnectedEdges(self):
        """
        Check each inpt and output socket to see if they have a connected edge. If so, update the positions of that edge.
        Useful for when we drag the node around and want the edges to follow.
        """
        for socket in (self.inputs + self.outputs):
            if socket.hasEdge():
                socket.edge.updatePositions()


    def remove(self):
        if DEBUG: print("> Removing Node", self)

        if DEBUG: print(" - remove all edges from sockets")
        for socket in (self.inputs+self.outputs):
            if socket.hasEdge():
                if DEBUG: print("    - removing from socket:", socket, "edge:", socket.edge)
                socket.edge.remove()

        if DEBUG: print(" - remove grNode")
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None

        if DEBUG: print(" - remove node from the scene")
        self.scene.removeNode(self)
        
        if DEBUG: print(" - everything was done.")


    def serialize(self):
        """ Returns the node's properties as a dict for easy serialization """
        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('inputs', [socket.serialize() for socket in self.inputs]),
            ('outputs', [socket.serialize() for socket in self.outputs]),
            ('content', self.content.serialize()),
        ])


    def deserialize(self, data, hashmap={}, restore_id=True):
        """ Given json-serialized data about the node, deserialize it and load it """
        if restore_id: self.id = data['id']

        hashmap[data['id']] = self

        self.setPos(data['pos_x'], data['pos_y'])
        self.title = data['title']

        data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000 )
        data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000 )

        # Deserialize data about the input and output sockets, and include it in the node data
        self.inputs = []
        for socket_data in data['inputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'], socket_type=socket_data['socket_type'])
            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.inputs.append(new_socket)

        self.outputs = []
        for socket_data in data['outputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'], socket_type=socket_data['socket_type'])
            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.outputs.append(new_socket)
