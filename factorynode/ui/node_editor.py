import json
from pathlib import Path

from PySide6.QtWidgets import (
    QGraphicsView,
    QApplication,
    QVBoxLayout,
    QLineEdit,
    QCompleter,
    QDialog,
)
from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import (
    QPainter,
    QCursor,
    QMouseEvent,
    QKeyEvent,
)

from ui.config import *
from ui.scene import Scene, Clipboard
from ui.node import Edge, EdgeWidget, NodeWidget, SocketWidget, NodeContent
from ui.machine import BaseManchine

NODE_TYPES = {"BaseMachine":BaseManchine}

class ContextMenu(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.start = False
        self.finish = False
        self.createWidgets()
        self.createLayout()
        self.createStyle()
        self.createConnections()
        self.search_node.setFocus()

    def createWidgets(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        self.search_node = QLineEdit()
        self.completer = QCompleter(NODE_TYPES.keys())
        self.search_node.setCompleter(self.completer)

    def createLayout(self):
        self.main_layout.addWidget(self.search_node)

    def createConnections(self):
        self.search_node.returnPressed.connect(self.onSelectedNode)
        self.completer.activated.connect(self.onSelectedNode)
        self.search_node.installEventFilter(self)

    def createStyle(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)

    def showEvent(self, event):
        self.setGeometry(QCursor.pos().x() - 100, QCursor.pos().y(), 100, 0)

    def mousePressEvent(self, event):
        self.close()

    def eventFilter(self, obj, event):
        if isinstance(obj, QLineEdit) and isinstance(event, QKeyEvent):
            if event.key() in [Qt.Key_Space, Qt.Key_Tab]:
                if self.start:
                    self.close()
                    return True

                else:
                    self.start = True

        return False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.close()

    def onSelectedNode(self):
        if not self.finish:
            self.parent.add_node(self.search_node.text())
            self.close()
            self.finish = True
        else:
            pass


class NodeEditorViewer(QGraphicsView):
    onNodeDoubleClicked = Signal(NodeContent)

    def __init__(self):
        super().__init__()
        self.mode = MODE_NOOP
        self.scene = Scene()
        self.clipboard = Clipboard(self.scene)
        self.zoom_in_factor = 1.25
        self.zoom_in_factor = 1.25
        self.zoom_clamp = True
        self.zoom = 4
        self.zoom_step = 1
        self.zoom_range = [-2, 8]
        self.last_node_selected = None
        self.setScene(self.scene.scene_widget)
        self.create_style()

    def create_style(self):
        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def add_node(self,type):
        NODE_TYPES[type](self.scene)

    def on_context_menu(self):
        pop_menu = ContextMenu(self)
        pop_menu.exec_()

    def on_edit_cut(self):
        data = self.clipboard.serializeSelected(delete=True)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def on_edit_copy(self):
        data = self.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def on_edit_paste(self):
        raw_data = QApplication.instance().clipboard().text()
        try:
            data = json.loads(raw_data)
        except:
            return
        if "nodes" not in data:
            return
        self.clipboard.deserializeFromClipboard(data)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):
        self.middle_press_position = event.localPos()
        releaseEvent = QMouseEvent(
            QEvent.MouseButtonRelease,
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            Qt.NoButton,
            event.modifiers(),
        )
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(
            event.type(),
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            event.buttons() | Qt.LeftButton,
            event.modifiers(),
        )
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(
            event.type(),
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            event.buttons() & ~Qt.LeftButton,
            event.modifiers(),
        )
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def mouseDoubleClickEvent(self, event):
        try:
            node_selected = self.scene.scene_widget.selectedItems()
            if len(node_selected) >= 1:
                node_selected = node_selected[0]
                if isinstance(node_selected, NodeWidget):
                    self.onNodeDoubleClicked.emit(node_selected.node.content)
                    if self.last_node_selected:
                        self.last_node_selected._is_open = False
                        self.last_node_selected.update()
                    self.last_node_selected = node_selected
                    node_selected._is_open = True
                    node_selected.update()

        except:
            pass
        super().mouseDoubleClickEvent(event)

    def leftMouseButtonPress(self, event):
        item = self.get_item_at_click(event)
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())
        if hasattr(item, "node") or isinstance(item, EdgeWidget) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(
                    event.type(),
                    event.localPos(),
                    event.screenPos(),
                    Qt.LeftButton,
                    Qt.NoButton,
                    event.modifiers() | Qt.ControlModifier,
                )

                super().mouseReleaseEvent(fakeEvent)
                return

        if type(item) is SocketWidget:
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edge_drag_start(item)
                return

        if self.mode == MODE_EDGE_DRAG:
            res = self.edge_drag_end(item)
            if res:
                return

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        item = self.get_item_at_click(event)
        if hasattr(item, "node") or isinstance(item, EdgeWidget) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(
                    event.type(),
                    event.localPos(),
                    event.screenPos(),
                    Qt.LeftButton,
                    Qt.NoButton,
                    event.modifiers() | Qt.ControlModifier,
                )

                super().mouseReleaseEvent(fakeEvent)
                return

            if self.dragMode() == QGraphicsView.RubberBandDrag:
                self.scene.history.storeHistory("Selection changed")

        if self.mode == MODE_EDGE_DRAG:
            if self.distance_between_click_and_release_is_off(event):
                res = self.edge_drag_end(item)
                if res:
                    return

        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.drag_edge.edge_widget.setDestination(pos.x(), pos.y())
            self.drag_edge.edge_widget.update()

        self.last_scene_mouse_position = self.mapToScene(event.pos())
        self.last_scale = float(
            str(self.viewportTransform()).split("(")[1].split(",")[0]
        )
        super().mouseMoveEvent(event)

    def event(self, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                self.on_context_menu()
                return False
            else:
                return super().event(event)
        else:
            return super().event(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            if not self.editing_flag:
                self.delete_selected()
            else:
                super().keyPressEvent(event)

        elif event.key() == Qt.Key_Tab:
            self.on_context_menu()
        elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            self.scene.save_to_file(f"{Path(__file__).parent.parent}/graph.json.txt")
        elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
            self.scene.load_from_file(f"{Path(__file__).parent.parent}/graph.json.txt")
        elif (
            event.key() == Qt.Key_Z
            and event.modifiers() & Qt.ControlModifier
            and not event.modifiers() & Qt.ShiftModifier
        ):
            self.scene.history.undo()
        elif (
            event.key() == Qt.Key_X
            and event.modifiers() & Qt.ControlModifier
            and not event.modifiers() & Qt.ShiftModifier
        ):
            self.on_edit_cut()
        elif (
            event.key() == Qt.Key_C
            and event.modifiers() & Qt.ControlModifier
            and not event.modifiers() & Qt.ShiftModifier
        ):
            self.on_edit_copy()
        elif (
            event.key() == Qt.Key_V
            and event.modifiers() & Qt.ControlModifier
            and not event.modifiers() & Qt.ShiftModifier
        ):
            self.on_edit_paste()
        elif (
            event.key() == Qt.Key_Y
            and event.modifiers() & Qt.ControlModifier
            and not event.modifiers() & Qt.ShiftModifier
        ):
            self.scene.history.redo()
        elif (
            event.key() == Qt.Key_H
            and event.modifiers() & Qt.ControlModifier
            and not event.modifiers() & Qt.ShiftModifier
        ):
            print(
                "HISTORY:     len(%d)" % len(self.scene.history.history_stack),
                " -- current_step",
                self.scene.history.history_current_step,
            )
            ix = 0
            for item in self.scene.history.history_stack:
                print("#", ix, "--", item["desc"])
                ix += 1

        else:
            super().keyPressEvent(event)

    def delete_selected(self):
        for item in self.scene.scene_widget.selectedItems():
            if isinstance(item, EdgeWidget):
                item.edge.remove()
            elif hasattr(item, "node"):
                item.node.remove()
            self.scene.history.storeHistory("Delete selected")

    def get_item_at_click(self, event):
        """return the object on which we've clicked/release mouse button"""
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def edge_drag_start(self, item):
        self.drag_start_socket = item.socket
        self.drag_edge = Edge(self.scene, item.socket, None)

    def edge_drag_end(self, item):
        self.mode = MODE_NOOP

        self.drag_edge.remove()
        self.drag_edge = None

        if type(item) is SocketWidget:
            if self.drag_start_socket.is_input != item.socket.is_input:
                if item.socket != self.drag_start_socket:
                    if item.socket.node != self.drag_start_socket.node:
                        if self.drag_start_socket.node.is_valid(
                            self.drag_start_socket.name, item.socket.name
                        ) or item.socket.node.is_valid(
                            item.socket.name, self.drag_start_socket.name
                        ):
                            if not item.socket.is_multi_edges:
                                item.socket.removeAllEdges()

                            if not self.drag_start_socket.is_multi_edges:
                                self.drag_start_socket.removeAllEdges()

                            if self.drag_start_socket.is_input:
                                new_edge = Edge(
                                    self.scene, self.drag_start_socket, item.socket
                                )
                                item.socket.node.transfer_data(
                                    node=self.drag_start_socket.node,
                                    input=self.drag_start_socket.name,
                                    output=item.socket.name,
                                )

                            else:
                                new_edge = Edge(
                                    self.scene, item.socket, self.drag_start_socket
                                )
                                self.drag_start_socket.node.transfer_data(
                                    node=item.socket.node,
                                    input=item.socket.name,
                                    output=self.drag_start_socket.name,
                                )

                        self.scene.history.storeHistory("Created new edge by dragging")
                        return True

        return False

    def distance_between_click_and_release_is_off(self, event):
        """measures if we are too far from the last LMB click scene position"""
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD * EDGE_DRAG_START_THRESHOLD
        return (
            dist_scene.x() * dist_scene.x() + dist_scene.y() * dist_scene.y()
        ) > edge_drag_threshold_sq

    def wheelEvent(self, event):
        zoom_out_factor = 1 / self.zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step

        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step

        clamped = False

        if self.zoom < self.zoom_range[0]:
            self.zoom, clamped = self.zoom_range[0], True
        if self.zoom > self.zoom_range[1]:
            self.zoom, clamped = self.zoom_range[1], True

        if not clamped or self.zoom_clamp is False:
            self.scale(zoom_factor, zoom_factor)
