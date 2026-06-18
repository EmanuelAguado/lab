import math
from collections import OrderedDict
from functools import partial
from pprint import pprint

from PySide6.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsItem,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QFrame,
    QSpacerItem,
    QGridLayout,
    QSizePolicy,
    QTextEdit,
    QMenu,
    QToolButton,
    QGraphicsTextItem
)
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (
    QPainterPath,
    QColor,
    QPalette,
    QPen,
    QBrush,
    QFont,
    QAction
)

from ui.config import *

class NameEdit(QWidget):
    def __init__(self, tokens=[], parent=None):
        super(NameEdit, self).__init__()

        self.create_widgets()
        self.create_layout()
        self.refreshMenu(tokens)

    def create_widgets(self):
        self.central_layout = QHBoxLayout(self)
        self.name_edit = QLineEdit()
        self.dropdown_var = QToolButton()

        self.pop_menu = QMenu()
        self.dropdown_var.setMenu(self.pop_menu)
        self.dropdown_var.setPopupMode(QToolButton.InstantPopup)

    def create_layout(self):
        self.central_layout.addWidget(self.name_edit)
        self.central_layout.addWidget(self.dropdown_var)

    def refreshMenu(self, tokens):
        self.pop_menu.clear()

        for token in tokens:
            self.pop_menu.addAction(
                QAction(token, self, triggered=partial(self.addToken, token))
            )

    def addToken(self, token):
        if self.name_edit.text() == "":
            self.name_edit.setText(token)
        else:
            self.name_edit.setText(self.name_edit.text() + "_" + token)

    def text(self):
        return self.name_edit.text()

    def setText(self, text):
        self.name_edit.setText(text)


class Serializable:
    def __init__(self):
        self.id = id(self)

    def serialize(self):
        raise NotImplemented()

    def deserialize(self, data, hashmap={}):
        raise NotImplemented()


class EdgeWidget(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge

        self._color = QColor("#FFFF7700")
        self._color_selected = QColor("#00ff00")
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen.setWidthF(8.0)
        self._pen_selected.setWidthF(2.0)
        self._pen_dragging.setWidthF(2.0)

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.setZValue(-1)

        self.posSource = [0, 0]
        self.posDestination = [200, 100]

    def calcPath(self):
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])

        return path

    def setSource(self, x, y):
        self.posSource = [x, y]

    def setDestination(self, x, y):
        self.posDestination = [x, y]

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calcPath()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.updatePath()

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def updatePath(self):
        s = self.posSource
        d = self.posDestination
        dist = (d[0] - s[0]) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        sspos = self.edge.start_socket.position

        if (s[0] > d[0] and sspos in (RIGHT_TOP, RIGHT_BOTTOM)) or (
            s[0] < d[0] and sspos in (LEFT_BOTTOM, LEFT_TOP)
        ):
            cpx_d *= -1
            cpx_s *= -1

            cpy_d = (
                (s[1] - d[1])
                / math.fabs((s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001)
            ) * EDGE_CP_ROUNDNESS
            cpy_s = (
                (d[1] - s[1])
                / math.fabs((d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001)
            ) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.cubicTo(
            s[0] + cpx_s,
            s[1] + cpy_s,
            d[0] + cpx_d,
            d[1] + cpy_d,
            self.posDestination[0],
            self.posDestination[1],
        )
        self.setPath(path)


class Edge(Serializable):
    def __init__(self, scene, start_socket=None, end_socket=None):
        super().__init__()
        self.scene = scene

        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket

        self.edge_widget = EdgeWidget(self)

        self.scene.scene_widget.addItem(self.edge_widget)
        if self.start_socket is not None:
            self.updatePositions()
        self.scene.add_edge(self)

    @property
    def start_socket(self):
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)

        self._start_socket = value
        if self.start_socket is not None:
            self.start_socket.add_edge(self)

    @property
    def end_socket(self):
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)

        self._end_socket = value
        if self.end_socket is not None:
            self.end_socket.add_edge(self)

    def serialize(self):
        try:
            return OrderedDict(
                [
                    ("id", self.id),
                    ("start", self.start_socket.id),
                    ("end", self.end_socket.id),
                ]
            )
        except:
            pass

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id:
            self.id = data["id"]
        self.start_socket = hashmap[data["start"]]
        self.end_socket = hashmap[data["end"]]

        if self.start_socket is not None:
            self.updatePositions()

        return True

    def updatePositions(self):
        source_pos = self.start_socket.get_socket_position()
        source_pos[0] += self.start_socket.node.node_widget.pos().x()
        source_pos[1] += self.start_socket.node.node_widget.pos().y()
        self.edge_widget.setSource(*source_pos)

        if self.end_socket is not None:
            end_pos = self.end_socket.get_socket_position()
            end_pos[0] += self.end_socket.node.node_widget.pos().x()
            end_pos[1] += self.end_socket.node.node_widget.pos().y()
            self.edge_widget.setDestination(*end_pos)
        else:
            self.edge_widget.setDestination(*source_pos)

        self.edge_widget.update()

    def remove_from_sockets(self):
        self.end_socket = None
        self.start_socket = None

    def remove(self):
        if self.end_socket:
            self.start_socket.node.content.delete_data(self.start_socket.name)
        self.remove_from_sockets()
        self.scene.scene_widget.removeItem(self.edge_widget)
        self.edge_widget = None
        try:
            self.scene.removeEdge(self)
        except:
            pass


class SocketWidget(QGraphicsItem):
    def __init__(self, socket, socket_type=1):
        self.socket = socket
        super().__init__(socket.node.node_widget)

        self._title_color = Qt.white
        self._title_font = QFont("Consolas", 8)

        self.radius = 6.0
        self.outline_width = 2.0
        self._color_background = QColor("#FFFF7700")
        self._color_hover_outline = QColor(QPalette().color(QPalette.Highlight))
        self._color_outline = QColor("#FF000000")

        self.width = 160
        self.name_horizontal_padding = 8.0

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)
        self.create_widgets()
        self.setAcceptHoverEvents(True)

    def create_widgets(self):
        self.name_socket = QGraphicsTextItem(self)
        self.name_socket.setDefaultTextColor(self._title_color)
        self.name_socket.setFont(self._title_font)
        self.name_socket.setPlainText(str(self.socket.name))
        self.name_socket.adjustSize()
        if self.socket.position in [LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM]:
            self.name_socket.setPos(
                self.name_horizontal_padding, -(2 * (self.radius + self.outline_width))
            )
        else:
            self.name_socket.setPos(
                -self.name_horizontal_padding - self.name_socket.textWidth(),
                -(2 * (self.radius + self.outline_width)),
            )

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # painting circle
        if not self.socket.node.node_widget.hide_sockets:
            painter.setBrush(self._brush)
            self._pen = QPen(self._color_outline)
            self._pen.setWidthF(self.outline_width)
            painter.setPen(self._pen)
            painter.drawEllipse(
                -self.radius, -self.radius, 2 * self.radius, 2 * self.radius
            )

    def boundingRect(self):
        return QRectF(
            -self.radius - self.outline_width,
            -self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )

    def hoverEnterEvent(self, event):
        self._color_outline = QColor(QPalette().color(QPalette.Highlight))
        self.outline_width = 4.0
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._color_outline = QColor("#FF000000")
        self.outline_width = 2.0
        super().hoverLeaveEvent(event)


class Socket(Serializable):
    def __init__(
        self,
        node,
        index=0,
        name="None",
        position=LEFT_CENTER,
        socket_type=1,
        multi_edges=True,
        count_on_this_node_side=1,
        is_input=False,
    ):
        super().__init__()

        self.edge = None
        self.node = node
        self.name = name
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.is_multi_edges = multi_edges
        self.count_on_this_node_side = count_on_this_node_side
        self.is_input = is_input
        self.is_output = not self.is_input

        self.socket_widget = SocketWidget(self, self.socket_type)

        self.socket_widget.setPos(*self.node.get_socket_position(index, position))

        self.setSocketPosition()

        self.edges = []

    def setSocketPosition(self):
        self.socket_widget.setPos(
            *self.node.get_socket_position(
                self.index, self.position, self.count_on_this_node_side
            )
        )

    def get_socket_position(self):
        return self.node.get_socket_position(
            self.index, self.position, self.count_on_this_node_side
        )

    def add_edge(self, edge):
        self.edges.append(edge)

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def removeAllEdges(self):
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove()

    def hasEdge(self):
        return self.edge is not None

    def serialize(self):
        return OrderedDict(
            [
                ("id", self.id),
                ("index", self.index),
                ("name", self.name),
                ("multi_edges", self.is_multi_edges),
                ("position", self.position),
                ("socket_type", self.socket_type),
            ]
        )

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id:
            self.id = data["id"]
        self.is_multi_edges = data["multi_edges"]
        hashmap[data["id"]] = self
        self.node.get_socket_position(
            self.index, self.position, self.count_on_this_node_side
        )


class NodeWidget(QGraphicsItem):
    def __init__(self, node, parent=None):
        super().__init__(parent)

        self.node = node
        self.content = self.node.content
        self.pin = False
        self.hide_sockets = False

        self._custom_name_color = QColor(150, 150, 150)
        self._title_color = Qt.white
        self._title_font = QFont("Consolas", 10)

        self.width = 160
        self.height = 100
        self.edge_roundness = 5.0
        self.edge_padding = 5.0
        self.title_height = 24.0
        self.title_horizontal_padding = 8.0
        self.title_vertical_padding = 8.0
        self._is_open = False

        self._pen_default = QPen(QColor(QPalette().color(QPalette.Base)))
        self._pen_selected = QPen(QColor(QPalette().color(QPalette.Highlight)))
        self._pen_open = QPen(QColor("#FFFF7700"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor(69, 69, 69, 230))

        self.create_widgets()
        self.createContent()
        self.create_style()
        self.create_connections()
        self.was_moved = False
        self.title = self.node.title

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height).normalized()

    def create_widgets(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)

        self.custom_name = QGraphicsTextItem(self)
        self.custom_name.setDefaultTextColor(self._custom_name_color)
        self.custom_name.setFont(self._title_font)
        self.custom_name.setPos(0, -30)
        self.custom_name.setTextWidth(self.width)
        self.custom_name.setPlainText(str("Empty name"))
        self.custom_name.setTextInteractionFlags(
            Qt.TextEditable | Qt.TextEditorInteraction | Qt.TextSelectableByMouse
        )
        self.custom_name.document().contentsChanged.connect(self.content.core)
        self.w = QWidget()
        self.l = QHBoxLayout(self.w)
        self.l.setContentsMargins(0, 0, 0, 0)
        self.l.setSpacing(0)
        self.btn_childrens = QPushButton("C")
        self.btn_childrens.setMinimumSize(24, 24)
        self.btn_childrens.setMaximumSize(24, 24)
        self.btn_pin = QPushButton("P")
        self.btn_pin.setMinimumSize(24, 24)
        self.btn_pin.setMaximumSize(24, 24)
        self.btn_hide_sockets = QPushButton("H")
        self.btn_hide_sockets.setMinimumSize(24, 24)
        self.btn_hide_sockets.setMaximumSize(24, 24)
        self.l.addWidget(self.btn_childrens)
        self.l.addWidget(self.btn_pin)
        self.l.addWidget(self.btn_hide_sockets)
        self.w.setGeometry(self.width - 72, 0, 72, 24)
        # self.btn_childrens.setPos(self.width, 0)

    def createContent(self):
        # self.widget_content = QGraphicsProxyWidget(self)
        # self.content.setGeometry(self.edge_padding, self.title_height + self.edge_padding,
        # self.width - 2*self.edge_padding, self.height - 2*self.edge_padding-self.title_height)

        self.grContent = self.node.scene.scene_widget.addWidget(self.w)
        self.grContent.node = self.node
        self.grContent.setParentItem(self)

    def create_connections(self):
        self.btn_childrens.clicked.connect(self.onChildren)
        self.btn_pin.clicked.connect(self.onPin)
        self.btn_hide_sockets.clicked.connect(self.onHideSockets)

    def create_style(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.btn_childrens.setCheckable(True)
        self.btn_pin.setCheckable(True)
        self.btn_hide_sockets.setCheckable(True)

    def onChildren(self):
        if self.btn_childrens.isChecked():
            self.hideChildren(self.node.inputs)

        else:
            self.showChildren(self.node.inputs)

    def onHideSockets(self):
        if self.btn_hide_sockets.isChecked():
            self.hide_sockets = True
            for socket in self.node.inputs + self.node.outputs:
                socket.socket_widget.hide()

        else:
            self.hide_sockets = False
            for socket in self.node.inputs + self.node.outputs:
                socket.socket_widget.show()

    def onPin(self):
        if self.btn_pin.isChecked():
            self.pin = True

        else:
            self.pin = False

    def hideChildren(self, inputs):
        for socket in inputs:
            for edge in socket.edges:
                edge.end_socket.node.node_widget.hide()
                edge.edge_widget.hide()
                if (
                    not edge.end_socket.node.inputs == []
                    and not edge.end_socket.node.node_widget.pin
                ):
                    self.hideChildren(edge.end_socket.node.inputs)

    def showChildren(self, inputs):
        for socket in inputs:
            for edge in socket.edges:
                edge.end_socket.node.node_widget.show()
                edge.edge_widget.show()
                if not edge.end_socket.node.inputs == []:
                    edge.end_socket.node.node_widget.btn_childrens.setChecked(False)
                    self.showChildren(edge.end_socket.node.inputs)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(
            0,
            0,
            self.width,
            self.title_height,
            self.edge_roundness,
            self.edge_roundness,
        )
        path_title.addRect(
            0,
            self.title_height - self.edge_roundness,
            self.edge_roundness,
            self.edge_roundness,
        )
        path_title.addRect(
            self.width - self.edge_roundness,
            self.title_height - self.edge_roundness,
            self.edge_roundness,
            self.edge_roundness,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(
            0,
            self.title_height,
            self.width,
            self.height - self.title_height,
            self.edge_roundness,
            self.edge_roundness,
        )
        path_content.addRect(
            0, self.title_height, self.edge_roundness, self.edge_roundness
        )
        path_content.addRect(
            self.width - self.edge_roundness,
            self.title_height,
            self.edge_roundness,
            self.edge_roundness,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(
            0, 0, self.width, self.height, self.edge_roundness, self.edge_roundness
        )

        if self.is_open():
            painter.setPen(self._pen_open)
        elif not self.isSelected():
            painter.setPen(self._pen_default)
        else:
            painter.setPen(self._pen_selected)

        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

    def is_open(self):
        return self._is_open 

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.node.update_connect_edges()

        for node in self.node.scene.nodes:
            if node.node_widget.isSelected():
                node.update_connect_edges()

        self.was_moved = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self.was_moved:
            self.was_moved = False
            self.node.scene.history.storeHistory("Node moved")


class NodeContent(QWidget, Serializable):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self._data = dict()
        self._out_data = dict()
        self.out_to_in = {}
        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.create_style()
        self.create_connections()

    def init_ui(self):
        self.central_layout = QVBoxLayout(self)
        self.title_label = QLabel(self.node.title)
        self.central_layout.addWidget(self.title_label)
        self.title_label.setStyleSheet(
            'font: 75 20pt "Consolas";text-decoration: underline;'
        )

    def add_content(self, name, widget):
        if not name in self._data.keys():
            if isinstance(
                widget, (QLineEdit, QLabel, QCheckBox, QComboBox, QSpinBox, NameEdit)
            ):
                self._data[name + "_label"] = QLabel(name)
            elif isinstance(widget, QFrame):
                self._data[name.split("_")[0] + "_label"] = QLabel(name)
            self._data[name] = widget

    def create_widgets(self):
        pass

    def create_layout(self):
        for name, widget in self._data.items():
            if isinstance(widget, QSpacerItem):
                self.central_layout.addItem(widget)

            elif isinstance(widget, (QHBoxLayout, QVBoxLayout, QGridLayout)):
                self.central_layout.addLayout(widget)
            else:
                self.central_layout.addWidget(widget)

        self.central_layout.addItem(
            QSpacerItem(5, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    def create_style(self):
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(5)

    def create_connections(self):
        for name, widget in self._data.items():
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.core)

            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self.core)

            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self.core)

            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self.core)

            elif isinstance(widget, NameEdit):
                widget.name_edit.textChanged.connect(self.core)

            # elif isinstance(widget,QTextEdit):

            #     widget.toPlainText()

    def set_editing_flags(self, value):
        self.node.scene.get_view().editing_flag = value

    def serialize(self):
        data = OrderedDict()
        for name, widget in self._data.items():
            if isinstance(widget, QLineEdit):
                data[name] = widget.text()

            elif isinstance(widget, QComboBox):
                data[name] = widget.currentText()

            elif isinstance(widget, QSpinBox):
                data[name] = widget.value()

            elif isinstance(widget, QCheckBox):
                data[name] = widget.isChecked()

            elif isinstance(widget, QTextEdit):
                data[name] = widget.toPlainText()

        return data

    def deserialize(self, data, hashmap={}):
        for name, value in data.items():
            if isinstance(self._data[name], QLineEdit):
                data[name] = self._data[name].setText(value)

            elif isinstance(self._data[name], QComboBox):
                data[name] = self._data[name].setCurrentText(value)

            elif isinstance(self._data[name], QSpinBox):
                data[name] = self._data[name].setValue(value)

            elif isinstance(self._data[name], QCheckBox):
                data[name] = self._data[name].setChecked(value)

            elif isinstance(self._data[name], QTextEdit):
                data[name] = self._data[name].setText(value)

    def check_connections(self):
        for output, input in self.out_to_in.items():
            for socket in self.node.inputs:
                if type(input) == type([]):
                    for item_input in input:
                        if socket.name == input:
                            if socket.edges == []:
                                self.delete_data(input)
                            else:
                                self.core()
                else:
                    if socket.name == input:
                        if socket.edges == []:
                            self.delete_data(input)
                        else:
                            self.core()

    def return_data(self, name):
        if name in self._out_data.keys():
            return self._out_data[name]
        else:
            return None

    def set_data(self, input, data):
        if type(input) == type([]):
            for item_input in input:
                if isinstance(self._data[item_input], QLineEdit):
                    self._data[item_input].setText(data)

                elif isinstance(self._data[item_input], QComboBox):
                    self._data[item_input].setCurrentText(data)

                elif isinstance(self._data[item_input], QSpinBox):
                    self._data[item_input].setValue(data)

                elif isinstance(self._data[item_input], QCheckBox):
                    self._data[item_input].setChecked(data)

                elif isinstance(self._data[item_input], QTextEdit):
                    self._data[item_input].setText(data)

        else:
            if isinstance(self._data[input], QLineEdit):
                self._data[input].setText(data)

            elif isinstance(self._data[input], QComboBox):
                self._data[input].setCurrentText(data)

            elif isinstance(self._data[input], QSpinBox):
                self._data[input].setValue(data)

            elif isinstance(self._data[input], QCheckBox):
                self._data[input].setChecked(data)

            elif isinstance(self._data[input], QTextEdit):
                self._data[input].setText(data)

    def delete_data(self, name):
        if isinstance(self._data[name], QLineEdit):
            self._data[name].setText("")

        elif isinstance(self._data[name], QComboBox):
            self._data[name].setCurrentIndex(0)

        elif isinstance(self._data[name], QSpinBox):
            self._data[name].setValue(0)

        elif isinstance(self._data[name], QCheckBox):
            self._data[name].setChecked(False)

        elif isinstance(self._data[name], QTextEdit):
            self._data[name].setText("")

    def is_valid(self, start_socket_name, end_socket_name):
        if end_socket_name in self.out_to_in.keys():
            if type(self.out_to_in[end_socket_name]) == type([]):
                if start_socket_name in self.out_to_in[end_socket_name]:
                    return True
            else:
                if self.out_to_in[end_socket_name] == start_socket_name:
                    return True

        return False

    def set_default_outputs(self):
        for socket in self.node.outputs:
            self._out_data[socket.name] = ""

    def core(self):
        for socket in self.node.outputs:
            for edge in socket.edges:
                if not edge.start_socket:
                    continue
                if edge.end_socket != socket:
                    continue
                edge.end_socket.node.transfer_data(
                    node=edge.start_socket.node,
                    input=edge.start_socket.node.content.out_to_in[socket.name],
                    output=socket.name,
                )

    def on_recursion(self, output):
        for socket in self.node.inputs:
            for edge in socket.edges:
                if not edge.start_socket:
                    continue
                if edge.start_socket != socket:
                    continue
                print(
                    "[ERROR DETECTED] DELETING EDGE:",
                    edge.start_socket.name,
                    "--->",
                    edge.end_socket.name,
                )
                edge.start_socket.removeEdge(edge)
                edge.end_socket.removeEdge(edge)
                edge.remove()


class Node(Serializable):
    def __init__(self, scene, title="Undefined Node", inputs=[], outputs=[]):
        super().__init__()
        self._title = title
        self.scene = scene
        self.inputs = []
        self.outputs = []
        self.content = self.init_contents()

        self.node_widget = NodeWidget(self)
        self.title = title

        self.scene.add_node(self)
        self.scene.scene_widget.addItem(self.node_widget)

        self.init_settings()
        self.init_socket(inputs, outputs)

        view = self.scene.get_view()
        center = view.mapToScene(view.rect().center())
        self.setPos(center.x(), center.y())

    def init_settings(self):
        self.socket_spacing = 22
        self.input_multi_edged = False
        self.output_multi_edged = True

    def init_contents(self):
        return self.content

    def init_socket(self, inputs, outputs, reset=True):
        counter = 0
        for item in inputs:
            socket = Socket(
                node=self,
                index=counter,
                name=item,
                position=LEFT_CENTER,
                multi_edges=self.input_multi_edged,
                count_on_this_node_side=len(inputs),
                is_input=True,
            )
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for item in outputs:
            socket = Socket(
                node=self,
                index=counter,
                name=item,
                position=RIGHT_CENTER,
                multi_edges=self.output_multi_edged,
                count_on_this_node_side=len(outputs),
                is_input=False,
            )
            counter += 1
            self.outputs.append(socket)
        self.content.set_default_outputs()

    def get_socket_position(self, index, position, num_out_of=1):
        x = (
            0
            if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM))
            else self.node_widget.width
        )

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = (
                self.node_widget.height
                - self.node_widget.edge_roundness
                - self.node_widget.title_horizontal_padding
                - index * self.socket_spacing
            )

        elif position in (LEFT_CENTER, RIGHT_CENTER):
            num_sockets = num_out_of
            node_height = self.node_widget.height
            top_offset = (
                self.node_widget.title_height
                + 2 * self.node_widget.title_vertical_padding
            )
            available_height = node_height - top_offset

            total_height_of_all_sockets = num_sockets * self.socket_spacing

            new_top = available_height - total_height_of_all_sockets

            y = top_offset + index * self.socket_spacing + new_top / 2

        elif position in (LEFT_TOP, RIGHT_TOP):
            # start from top
            y = (
                self.node_widget.title_height
                + self.node_widget.title_vertical_padding
                + self.node_widget.edge_roundness
                + index * self.socket_spacing
            )
        else:
            y = 0

        return [x, y]

    def is_valid(self, input, output):
        return self.content.is_valid(input, output)

    def transfer_data(self, node, output, input):
        data = self.content.return_data(output)
        node.content.set_data(input, data)

    @property
    def pos(self):
        return self.node_widget.pos()

    def setPos(self, x, y):
        self.node_widget.setPos(x, y)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.node_widget.title = self._title
        self.content.title_label.setText(self._title)

    def update_connect_edges(self):
        for socket in self.inputs + self.outputs:
            # if socket.hasEdge():
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self):
        for socket in self.inputs + self.outputs:
            for edge in socket.edges:
                edge.remove()

        self.scene.scene_widget.removeItem(self.node_widget)
        self.node_widget = None
        self.scene.removeNode(self)

    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs:
            inputs.append(socket.serialize())
        for socket in self.outputs:
            outputs.append(socket.serialize())
        return OrderedDict(
            [
                ("id", self.id),
                ("title", self.title),
                ("custom_name", self.node_widget.custom_name.toPlainText()),
                ("pos_x", self.node_widget.scenePos().x()),
                ("pos_y", self.node_widget.scenePos().y()),
                ("class", self.__class__.__name__),
                ("inputs", inputs),
                ("outputs", outputs),
                ("content", self.content.serialize()),
            ]
        )

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id:
            self.id = data["id"]
        hashmap[data["id"]] = self

        self.setPos(data["pos_x"], data["pos_y"])
        self.title = data["title"]
        self.node_widget.custom_name.setPlainText(data["custom_name"])

        data["inputs"].sort(
            key=lambda socket: socket["index"] + socket["position"] * 10000
        )
        data["outputs"].sort(
            key=lambda socket: socket["index"] + socket["position"] * 10000
        )

        self.inputs = []
        for socket_data in data["inputs"]:
            new_socket = Socket(
                node=self,
                index=socket_data["index"],
                name=socket_data["name"],
                position=socket_data["position"],
                multi_edges=socket_data["multi_edges"],
                count_on_this_node_side=len(data["inputs"]),
                is_input=True,
            )

            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.inputs.append(new_socket)

        self.outputs = []
        for socket_data in data["outputs"]:
            new_socket = Socket(
                node=self,
                index=socket_data["index"],
                name=socket_data["name"],
                position=socket_data["position"],
                multi_edges=socket_data["multi_edges"],
                count_on_this_node_side=len(data["outputs"]),
                is_input=False,
            )

            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.outputs.append(new_socket)
        res = self.content.deserialize(data["content"], hashmap)

        # return True & res
