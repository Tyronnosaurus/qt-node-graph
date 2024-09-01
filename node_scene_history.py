from node_graphics_edge import QDMGraphicsEdge


DEBUG = False


class SceneHistory():
    """ History of changes for undo/redo feature. Implemented as a stack. """

    def __init__(self, scene):
        self.scene = scene

        self.history_stack = []
        self.history_current_step = -1  # Index of most recent action in history_stack
        self.history_limit = 32


    def undo(self):
        if (self.history_current_step > 0):
            if DEBUG: print("UNDO")
            self.history_current_step -= 1
            self.restoreHistory()
        else:
            if DEBUG: print("Nothing to undo")


    def redo(self):
        if (self.history_current_step + 1 < len(self.history_stack)):
            if DEBUG: print("REDO")
            self.history_current_step += 1
            self.restoreHistory()
        else:
            if DEBUG: print("Nothing to redo")


    def restoreHistory(self):
        """  """
        if DEBUG: print(f"Restoring history .... current_step: {self.history_current_step} ({len(self.history_stack)})")
        self.restoreHistoryStamp(self.history_stack[self.history_current_step])


    def storeHistory(self, desc, setModified=False):
        """  """
        if setModified:
            self.scene.has_been_modified = True

        if DEBUG: print(f"Storing history '{desc}' .... current_step: @{self.history_current_step} ({len(self.history_stack)})")

        # If the pointer (history_current_step) is not at the end of history_stack
        if (self.history_current_step+1 < len(self.history_stack)):
            self.history_stack = self.history_stack[0:self.history_current_step+1]

        # History is outside of the limits
        if (self.history_current_step + 1 >= self.history_limit):
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1

        hs = self.createHistoryStamp(desc)

        self.history_stack.append(hs)
        self.history_current_step += 1
        if DEBUG: print("  -- setting step to:", self.history_current_step)


    def createHistoryStamp(self, desc):
        """ Returns a serialized snapshot of all nodes and edges in the scene """
        sel_obj = {
            'nodes': [],
            'edges': [],
        }

        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_obj['nodes'].append(item.node.id)
            elif isinstance(item, QDMGraphicsEdge):
                sel_obj['edges'].append(item.edge.id)

        history_stamp = {
            'desc': desc,
            'snapshot': self.scene.serialize(),
            'selection': sel_obj,
        }

        return history_stamp


    def restoreHistoryStamp(self, history_stamp):
        """  """
        if DEBUG: print("Restore history stamp: ", history_stamp['desc'])

        self.scene.deserialize(history_stamp['snapshot'])

        # Restore selection
        for edge_id in history_stamp['selection']['edges']:
            for edge in self.scene.edges:
                if (edge.id == edge_id):
                    edge.grEdge.setSelected(True)
                    break

        for node_id in history_stamp['selection']['nodes']:
            for node in self.scene.nodes:
                if (node.id == node_id):
                    node.grNode.setSelected(True)
                    break
