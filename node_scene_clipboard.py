from collections import OrderedDict
from node_graphics_edge import QDMGraphicsEdge
from node_node import Node
from node_edge import Edge
from sys import float_info


DEBUG = False


class SceneClipboard():
    """ Stores serialized data about copied and cut elements """
    
    def __init__(self, scene):
        self.scene = scene

    def serializeSelected(self, delete=False):
        if DEBUG: print("--- COPY TO CLIPBOARD ---")

        sel_nodes, sel_edges, sel_sockets = [], [], {}

        # Sort edges and nodes
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_nodes.append(item.node.serialize())
                for socket in (item.node.inputs + item.node.outputs):
                    sel_sockets[socket.id] = socket
            elif isinstance(item, QDMGraphicsEdge):
                sel_edges.append(item.edge)

        # Debug
        if DEBUG:
            print("  NODES\n      ", sel_nodes)
            print("  EDGES\n      ", sel_edges)
            print("  SOCKETS\n     ", sel_sockets)

        # Remove all edges which are not connected to a node in our list
        edges_to_remove = []
        for edge in sel_edges:
            if (edge.start_socket.id in sel_sockets and edge.end_socket.id in sel_sockets):
                # if DEBUG: print(" edge is ok, connected with both sides")
                pass
            else:
                if DEBUG: print("edge", edge, "is not connected with both sides")
                edges_to_remove.append(edge)
        for edge in edges_to_remove:
            sel_edges.remove(edge)

        # Make final list of edges
        edges_final = []
        for edge in sel_edges:
            edges_final.append(edge.serialize())

        if DEBUG: print("our final edge list:", edges_final)

        data = OrderedDict([
            ('nodes', sel_nodes),
            ('edges', edges_final),
        ])

        # If CUT (aka delete) remove selected items
        if delete:
            self.scene.grScene.views()[0].deleteSelected()
            # Store change in history for undo
            self.scene.history.storeHistory("Cut out elements from scene", setModified=True)

        return data


    def deserializeFromClipboard(self, data):
        """
        Given serialized data about nodes and edges, recreates them in the scene,
        but in the current mouse position rather than their original position. 
        """
        hashmap = {}

        # Calculate mouse pointer - scene position
        view = self.scene.grScene.views()[0]
        mouse_scene_pos = view.last_scene_mouse_position

        # Calculate selected objects bbox and center
        minx, maxx, miny, maxy = float_info.max, float_info.min, float_info.max, float_info.min
        for node_data in data['nodes']:
            x, y = node_data['pos_x'], node_data['pos_y']
            if (x < minx): minx = x
            if (x > maxx): maxx = x
            if (y < miny): miny = y
            if (y > maxy): maxy = y
        bbox_center_x = (minx + maxx) / 2
        bbox_center_y = (miny + maxy) / 2

        # center = view.mapToScene(view.rect().center())

        # Calculate the offset of the newly created nodes
        offset_x = mouse_scene_pos.x() - bbox_center_x
        offset_y = mouse_scene_pos.y() - bbox_center_y

        # Create each node
        for node_data in data['nodes']:
            new_node = Node(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False)

            # Read just the new node's position
            pos = new_node.pos
            new_node.setPos(pos.x() + offset_x, pos.y() + offset_y)

        # Create each edge
        if 'edges' in data:
            for edge_data in data['edges']:
                new_edge = Edge(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False)

        # Store history
        self.scene.history.storeHistory("Pasted elements in scene", setModified=True)
