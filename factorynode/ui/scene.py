from collections import OrderedDict
import json
import math
import pprint

from PySide6.QtWidgets import (
    QGraphicsScene,
)
from PySide6.QtCore import QLine
from PySide6.QtGui import (
    QColor,
    QPalette,
    QPen,
)

from ui.config import *
from ui.node import Edge, EdgeWidget, Serializable
from ui.machine import BaseManchine

class Clipboard:
    def __init__(self, scene):
        self.scene = scene

    def serializeSelected(self, delete=False):
        sel_nodes, sel_edges, sel_sockets = [], [], {}
        for item in self.scene.scene_widget.selectedItems():
            if hasattr(item, "node"):
                sel_nodes.append(item.node.serialize())
                for socket in item.node.inputs + item.node.outputs:
                    sel_sockets[socket.id] = socket
            elif isinstance(item, EdgeWidget):
                sel_edges.append(item.edge)

        edges_to_remove = []
        for edge in sel_edges:
            if (
                edge.start_socket.id in sel_sockets
                and edge.end_socket.id in sel_sockets
            ):
                pass
            else:
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            sel_edges.remove(edge)

        edges_final = []
        for edge in sel_edges:
            edges_final.append(edge.serialize())

        data = OrderedDict(
            [
                ("nodes", sel_nodes),
                ("edges", edges_final),
            ]
        )

        if delete:
            self.scene.get_view().deleteSelected()

            self.scene.history.storeHistory("Cut out elemets from scene")

        return data

    def deserializeFromClipboard(self, data):
        hashmap = {}

        view = self.scene.get_view()
        mouse_scene_pos = view.last_scene_mouse_position

        minx, maxx, miny, maxy = 0, 0, 0, 0
        for node_data in data["nodes"]:
            x, y = node_data["pos_x"], node_data["pos_y"]
            if x < minx:
                minx = x
            if x < maxx:
                maxx = x
            if y < miny:
                miny = y
            if y < maxy:
                maxy = y
            if x < minx:
                minx = x

        mousex, mousey = mouse_scene_pos.x(), mouse_scene_pos.y()

        maxx -= 180
        maxy += 100

        bbox_center_x = (minx + maxx) / 2
        bbox_center_y = (miny + maxy) / 2

        offset_x = mouse_scene_pos.x() - bbox_center_x
        offset_y = mouse_scene_pos.y() - bbox_center_y

        nodes = []
        for node_data in data["nodes"]:
            new_node = eval(node_data["class"])(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False)

            # pos = new_node.pos
            # new_node.setPos(view.last_scene_mouse_position.x(),view.last_scene_mouse_position.y())
            nodes.append(new_node)

            posx, posy = new_node.pos.x(), new_node.pos.y()
            newx, newy = mousex + posx - minx, mousey + posy - miny

            new_node.setPos(newx, newy)

        if "edges" in data:
            for edge_data in data["edges"]:
                new_edge = Edge(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False)

        for node in nodes:
            node.content.check_connections()

        self.scene.history.storeHistory("Pasted elements in scene")

        return


class SceneHistory:
    def __init__(self, scene):
        self.scene = scene

        self.history_stack = []
        self.history_current_step = -1
        self.history_limit = 32

    def undo(self):
        if self.history_current_step > 0:
            self.history_current_step -= 1
            self.restoreHistory()

    def redo(self):
        if self.history_current_step + 1 < len(self.history_stack):
            self.history_current_step += 1
            self.restoreHistory()

    def restoreHistory(self):
        self.restoreHistoryStamp(self.history_stack[self.history_current_step])

    def storeHistory(self, desc):
        # if the pointer (history_current_step) is not at the end of history_stack
        if self.history_current_step + 1 < len(self.history_stack):
            self.history_stack = self.history_stack[0 : self.history_current_step + 1]

        # history is outside of the limits
        if self.history_current_step + 1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1

        hs = self.createHistoryStamp(desc)

        self.history_stack.append(hs)
        self.history_current_step += 1

    def createHistoryStamp(self, desc):
        sel_obj = {
            "nodes": [],
            "edges": [],
        }
        for item in self.scene.scene_widget.selectedItems():
            if hasattr(item, "node"):
                sel_obj["nodes"].append(item.node.id)
            elif isinstance(item, EdgeWidget):
                sel_obj["edges"].append(item.edge.id)

        history_stamp = {
            "desc": desc,
            "snapshot": self.scene.serialize(),
            "selection": sel_obj,
        }

        return history_stamp

    def restoreHistoryStamp(self, history_stamp):
        self.scene.deserialize(history_stamp["snapshot"])

        # restore selection
        for edge_id in history_stamp["selection"]["edges"]:
            for edge in self.scene.edges:
                if edge.id == edge_id:
                    edge.edge_widget.setSelected(True)
                    break

        for node_id in history_stamp["selection"]["nodes"]:
            for node in self.scene.nodes:
                if node.id == node_id:
                    node.node_widget.setSelected(True)
                    break


class Scene(Serializable):
    def __init__(self):
        super().__init__()

        self.nodes = []
        self.edges = []
        self.node_class_selector = None
        self.create_widgets()
        self.history = SceneHistory(self)

    def create_widgets(self):
        self.scene_widget = NodeEditorScene(self)

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

    def save_to_file(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        print("saving to", filename, "was successfull.")

    def load_from_file(self, filename):
        with open(filename, "r") as file:
            raw_data = file.read()
            data = json.loads(raw_data)
            self.deserialize(data)

    def get_item_at(self, pos):
        return self.get_view().itemAt(pos)

    def get_view(self):
        return self.scene_widget.views()[0]

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes:
            nodes.append(node.serialize())
        for edge in self.edges:
            edges.append(edge.serialize())
        return OrderedDict(
            [
                ("id", self.id),
                ("nodes", nodes),
                ("edges", edges),
            ]
        )

    def deserialize(self, data, hashmap={}, restore_id=True):
        self.clear()

        hashmap = {}

        if restore_id:
            self.id = data["id"]

        for node_data in data["nodes"]:
            eval(node_data["class"])(self).deserialize(node_data, hashmap, restore_id)
        for edge_data in data["edges"]:
            pprint.pprint(edge_data)
            pprint.pprint(hashmap)
            pprint.pprint(restore_id)
            Edge(self).deserialize(edge_data, hashmap, restore_id)

        return True


class NodeEditorScene(QGraphicsScene):
    def __init__(self, scene):
        super().__init__()

        self.scene_core = scene
        
        self.scene_width = 64000
        self.scene_height = 64000
        self.set_grid_scene(self.scene_width,self.scene_height)

        self.grid_size = 20
        self.grid_squares = 5

        self.bg_color = QColor(QPalette().color(QPalette.Base))
        self.light_color = QColor(QPalette().color(QPalette.Window))
        self.dark_color = QColor(QPalette().color(QPalette.Window))

        self.pen_light = QPen(self.light_color)
        self.pen_light.setWidth(1)
        self.pen_dark = QPen(self.dark_color)
        self.pen_dark.setWidth(2)

        self.setBackgroundBrush(self.bg_color)

    def set_grid_scene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # here we create our grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        lines_light = []
        lines_dark = []

        for x in range(first_left, right, self.grid_size):
            if x % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if y % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        # draw the lines
        painter.setPen(self.pen_light)
        painter.drawLines(lines_light)

        painter.setPen(self.pen_dark)
        painter.drawLines(lines_dark)


