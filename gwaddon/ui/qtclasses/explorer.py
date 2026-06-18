from os import fspath
from functools import partial
from pathlib import Path
from shutil import copy2, copytree, move
from PySide6.QtCore import (
    Qt,
    QModelIndex,
    QTimer,
    QVariantAnimation,
    QAbstractAnimation,
)
from PySide6.QtGui import (
    QColor,
    QPalette,
    QIcon,
    QKeySequence,
    QAction,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QMenu,
    QToolButton,
    QSizePolicy,
    QComboBox,
    QTreeView,
    QFileSystemModel,
    QGridLayout,
    QAbstractItemView,
    QHeaderView,
    QScrollArea,
    QPushButton,
)


class AToolButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation = None

    def setAnimation(self, time=0, valueA="", valueB=""):
        self._animation = QVariantAnimation(self)
        self._animation.valueChanged.connect(self._animate)
        self._animation.setStartValue(QColor(valueA))
        self._animation.setEndValue(QColor(valueB))
        self._animation.setDuration(time)

    def _animate(self, value):
        style = (
            "*{background-color: " + value.name() + ";border:None;padding-right:14px}"
            "*::menu-button {background-color: palette(base)}"
            "*::menu-arrow {image: url(./gwaddon/utils/static/icons/explorer_bar.png)} "
            "*::menu-button:hover {background-color: palette(highlight);border-left:2px solid palette(base);}"
            "*:checked{background-color:palette(highlight)}"
            "*::menu-arrow:open {image: url(./gwaddon/utils/static/icons/explorer_bar.png)}"
        )
        self.setStyleSheet(style)

    def enterEvent(self, event):
        if self._animation:
            self._animation.setDirection(QAbstractAnimation.Forward)
            self._animation.start()
            super().enterEvent(event)

    def leaveEvent(self, event):
        if self._animation:
            self._animation.setDirection(QAbstractAnimation.Backward)
            self._animation.start()
            super().leaveEvent(event)


class ComboPath(QScrollArea):
    def __init__(self, path: Path, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.path = path
        self.create_widgets()

    def create_widgets(self):
        widget = QWidget()
        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout = QHBoxLayout(widget)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setSpacing(0)
        self.folder = dict()
        self.sub_menu = dict()
        for code, token in enumerate(self.path.parts, start=1):
            path = Path(*self.path.parts[:code])
            self.folder[code] = AToolButton()
            self.folder[code].setAnimation(
                250,
                QPalette().color(QPalette.Base).name(),
                QPalette().color(QPalette.Highlight).name(),
            )
            self.folder[code].setText(token.rstrip("/\\"))
            self.folder[code].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            self.folder[code].clicked.connect(partial(self.add_item, path))
            self.folder[code].setPopupMode(QToolButton.MenuButtonPopup)
            self.sub_menu[code] = QMenu()
            self.sub_menu[code].aboutToShow.connect(
                partial(self.create_submenu, code, path)
            )
            self.folder[code].setMenu(self.sub_menu[code])
            self.horizontal_layout.addWidget(self.folder[code])
            self.folder[code].setMinimumWidth(
                self.folder[code]
                .fontMetrics()
                .boundingRect(self.folder[code].text())
                .width()
                + 25
            )

        self.b_close = QPushButton()
        self.b_close.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.b_close.clicked.connect(self.on_close)
        self.b_close.setMinimumWidth(10)
        self.b_close.setStyleSheet("background-color:palette(base)")
        self.b_close.setCursor(Qt.PointingHandCursor)
        self.horizontal_layout.addWidget(self.b_close)
        self.setStyleSheet(
            "QScrollArea{background-color:palette(base);margin-right:24px}"
        )

    def create_submenu(self, code: int, path: Path):
        list_path = [p for p in path.glob("*") if p.is_dir()]
        if not list_path:
            return
        for file_path in list_path:
            self.sub_menu[code].addAction(
                QAction(
                    fspath(file_path),
                    self,
                    triggered=partial(self.add_item, file_path),
                )
            )

    def add_item(self, path: Path, *args):
        self.parent.parent.set_path(path)
        self.close()

    def resizeEvent(self, event):
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().maximum())
        super().resizeEvent(event)

    def on_close(self):
        self.parent.lineEdit().selectAll()
        self.parent.delete_combo_path()


class PathEditor(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.create_header_widget()
        self.combo_path_flag = False
        self.list_items = []

    def create_header_widget(self):
        self.setEditable(True)
        self.lineEdit().returnPressed.connect(
            lambda: self.parent.set_path(Path(self.lineEdit().text()))
        )
        self.currentIndexChanged.connect(self.change_path)
        self.activated.connect(
            lambda: self.parent.set_path(Path(self.lineEdit().text()))
        )
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.setStyleSheet(
            "*{background: palette(base);border: 0px} "
            "*::drop-down {background: palette(base);border: 0px;padding-right:4px;padding-left:4px} "
            "*::down-arrow {background: palette(base);image: url(./gwaddon/utils/static/icons/down.png); height: 14px;width:14px;} "
            "*::down-arrow:hover {background: palette(highlight);image: url(./gwaddon/utils/static/icons/down.png); height: 14px;width:14px;} "
            "*::drop-down:hover{background-color:palette(highlight)}"
        )

    def set_path(self, path: Path):
        str_path = fspath(path)
        if str_path not in self.list_items:
            self.addItem(str_path)
            self.list_items.append(str_path)
        self.setCurrentIndex(self.findText(str_path))

    def change_path(self):
        self.delete_combo_path()
        self.create_combo_path()

    def focusOutEvent(self, event):
        if self.combo_path_flag:
            self.change_path()

    def resizeEvent(self, event):
        if self.combo_path_flag:
            self.combo_path.move(0, 0)
            self.combo_path.resize(self.width(), self.height())
        super().resizeEvent(event)

    def create_combo_path(self):
        self.combo_path = ComboPath(Path(self.currentText()), self)
        self.combo_path.move(0, 0)
        self.combo_path.resize(self.width(), self.height())
        self.combo_path_flag = True
        self.combo_path.show()

    def delete_combo_path(self):
        if self.combo_path_flag:
            self.combo_path.close()
            self.combo_path_flag = False


class FileSystemModel(QFileSystemModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cut_select = None

    def paint_cut(self, item):
        self.cut_select = item
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    def data(self, index, role=Qt.DisplayRole):
        if self.cut_select and role == Qt.ForegroundRole:
            if self.cut_select == super().filePath(index):
                return QColor("grey")
        return super().data(index, role)


class TreeView(QTreeView):
    def focusInEvent(self, event):
        for sc in self.parent().findChildren(QShortcut):
            sc.setEnabled(True)

    def focusOutEvent(self, event):
        for sc in self.parent().findChildren(QShortcut):
            sc.setEnabled(False)


class Explorer(QWidget):
    def __init__(self):
        super().__init__()
        self.history = {}
        self.code_history = 0
        self.timer_value = False
        self.select_file = None
        self.cut_mode = False
        self.clipboard: list[Path] = list()
        self.setup_ui()
        self.create_shortcuts()
        self.create_context_menu()

    def setup_ui(self):
        self.grid_central = QGridLayout(self)
        self.grid_central.setContentsMargins(0, 0, 0, 0)
        self.grid_central.setHorizontalSpacing(0)
        self.grid_central.setVerticalSpacing(1)
        self.path_editor = PathEditor(self)
        self.grid_central.addLayout(self.create_header(), 1, 0)
        self.grid_central.addWidget(self.create_tree_view())

    def create_tool_button(self, icon, callback, size=(24, 32)):
        button = QToolButton()
        button.setIcon(QIcon(icon))
        button.setAutoRaise(True)
        button.setMaximumSize(*size)
        button.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        button.clicked.connect(callback)
        return button

    def create_header(self):
        header_layout = QHBoxLayout()
        icons_callbacks = [
            (
                "./gwaddon/utils/static/icons/back.png",
                self.down_history,
            ),
            (
                "./gwaddon/utils/static/icons/forward.png",
                self.up_history,
            ),
            (
                "./gwaddon/utils/static/icons/up.png",
                self.set_parent_path,
            ),
            (
                "./gwaddon/utils/static/icons/refresh.png",
                self.refresh,
            ),
        ]

        for icon, callback in icons_callbacks:
            header_layout.addWidget(self.create_tool_button(icon, callback))

        header_layout.addWidget(self.path_editor)
        return header_layout

    def create_tree_view(self):
        self.tree_view = TreeView(self)
        self.create_model()
        self.tree_view.setItemsExpandable(False)
        self.tree_view.setSelectionMode(QTreeView.ExtendedSelection)
        self.tree_view.setDragDropMode(QAbstractItemView.DragDrop)
        self.tree_view.setDefaultDropAction(Qt.MoveAction)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree_view.setAcceptDrops(True)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.header().resizeSections(QHeaderView.ResizeToContents)
        self.tree_view.header().setDefaultAlignment(Qt.AlignVCenter)
        self.tree_view.clicked.connect(self.on_click)
        self.tree_view.doubleClicked.connect(self.on_double_click)
        self.tree_view.customContextMenuRequested.connect(self.on_context_menu)
        return self.tree_view

    def create_model(self):
        self.model_view = FileSystemModel()
        self.model_view.setReadOnly(False)
        self.model_view.directoryLoaded.connect(self.expand_items)
        self.tree_view.setModel(self.model_view)

    def expand_items(self):
        self.tree_view.header().resizeSections(QHeaderView.ResizeToContents)

    def create_context_menu(self):
        self.pop_menu = QMenu(self)
        actions = [
            ("Copy path", self.on_clipboard),
            ("Separator", None),
            ("New folder", self.new_folder),
            ("Separator", None),
            ("Cut", lambda: self.copy(True)),
            ("Copy", self.copy),
            ("Paste", self.paste),
            ("Duplicate", self.duplicate),
            (
                "Rename",
                lambda: self.tree_view.edit(self.tree_view.selectedIndexes()[0]),
            ),
            ("Delete", self.remove),
        ]

        for name, callback in actions:
            if name == "Separator":
                self.pop_menu.addSeparator()
            else:
                self.pop_menu.addAction(QAction(name, self, triggered=callback))

    def create_shortcuts(self):
        shortcuts = [
            (Qt.Key_Backspace, self.tree_view, self.down_history),
            ("Ctrl+X", self.tree_view, lambda: self.copy(True)),
            ("Ctrl+C", self.tree_view, self.copy),
            ("Ctrl+V", self.tree_view, self.paste),
            ("Ctrl+D", self.tree_view, self.duplicate),
            ("Ctrl+Shift+N", self.tree_view, self.new_folder),
            ("Ctrl+Shift+C", self.tree_view, self.on_clipboard),
            ("Enter", self.tree_view, self.on_double_click),
            ("Return", self.tree_view, self.on_double_click),
            (
                "F2",
                self.tree_view,
                lambda: self.tree_view.edit(self.tree_view.selectedIndexes()[0]),
            ),
            (Qt.Key_Delete, self.tree_view, self.remove),
        ]

        for key, widget, callback in shortcuts:
            QShortcut(QKeySequence(key), widget, callback)

    def on_clipboard(self):
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return
        index = indexes[0]
        clipb_text = self.model_view.filePath(index)
        clipboard = QApplication.clipboard()
        clipboard.setText(clipb_text)

    def copy(self, cut: bool = False):
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return
        self.clipboard = []
        for index in indexes:
            file = self.model_view.filePath(index)
            if index.column() == 0:
                self.clipboard.append(Path(file))
                self.model_view.paint_cut(file)
        self.cut_mode = cut

    def paste(self):
        destination = Path(self.path_editor.currentText())
        for path in self.clipboard:
            target = destination / path.name
            counter = 1
            while target.exists():
                target = destination / f"{path.stem}_COPY{counter}{path.suffix}"
                counter += 1
            if self.cut_mode:
                move(str(path), str(target))
            else:
                if path.is_dir():
                    copytree(path, target)
                else:
                    copy2(path, target)
        self.clipboard.clear()
        self.cut_mode = False

    def duplicate(self):
        index = self.tree_view.selectedIndexes()[0]
        file = Path(self.model_view.filePath(index))
        counter = 1
        new_file = file.parent / f"{file.stem}_COPY{counter}_{file.suffix}"
        while new_file.exists():
            counter += 1
            new_file = file.parent / f"{file.stem}_COPY{counter}_{file.suffix}"
        copy2(file, new_file)

    def remove(self):
        for index in self.tree_view.selectedIndexes():
            if index.column() == 0:
                self.model_view.remove(index)

    def new_folder(self):
        base_path = self.path_editor.currentText()
        code = 1
        new_folder = Path(base_path, "New Folder")
        while new_folder.exists():
            new_folder = Path(base_path, f"New Folder_{code}")
            code += 1
        new_folder.mkdir(parents=True)
        self.tree_view.edit(self.model_view.index(fspath(new_folder)))

    def on_context_menu(self, point):
        self.pop_menu.exec(self.tree_view.mapToGlobal(point))

    def on_click(self, index):
        file = self.model_view.filePath(index)
        if self.select_file == file and not self.timer_value:
            self.tree_view.edit(self.model_view.index(file))
            self.select_file = None
        else:
            self.timer_value = True
            self.timer_rename = QTimer()
            self.timer_rename_out = QTimer()
            self.timer_rename.timeout.connect(lambda: self.update_caption("in"))
            self.timer_rename_out.timeout.connect(lambda: self.update_caption("out"))
            self.timer_rename.start(500)
            self.timer_rename_out.start(1000)
            self.select_file = file

    def on_double_click(self, *args):
        index = self.tree_view.selectedIndexes()[0]
        path = Path(self.model_view.filePath(index))
        if path.is_dir():
            self.set_path(path)
        else:
            self.open()

    def set_parent_path(self):
        parent_path = Path(self.path_editor.currentText()).parent
        self.set_path(parent_path)

    def down_history(self):
        if self.code_history > 1:
            self.code_history -= 1
            self.set_path(Path(self.history[self.code_history]), False)

    def up_history(self):
        if self.code_history < len(self.history):
            self.code_history += 1
            self.set_path(Path(self.history[self.code_history]), False)

    def add_history(self, path: Path):
        self.code_history += 1
        self.history[self.code_history] = fspath(path)
        self.history = {k: v for k, v in self.history.items() if k <= self.code_history}

    def remove_history(self):
        self.history = dict()

    def refresh(self):
        current_path = Path(self.path_editor.currentText())
        self.create_model()
        self.set_path(current_path)

    def open(self):
        index = self.tree_view.selectedIndexes()[0]
        file = self.model_view.filePath(index)
        # subprocess.Popen(os.path.basename(file), shell=True, cwd=os.path.dirname(file))

    def update_caption(self, logic):
        if logic == "in":
            self.timer_rename.stop()
            self.timer_value = False
        elif logic == "out":
            self.timer_rename_out.stop()
            self.timer_value = True

    def set_path(self, path: Path, add_history: bool = True):
        if not path.is_dir():
            path = path.parent
        root = path.drive
        self.model_view.setRootPath(root)
        self.tree_view.setRootIndex(self.model_view.index(fspath(path)))
        self.path_editor.set_path(path)
        if add_history:
            self.add_history(path)
        self.tree_view.header().resizeSections(QHeaderView.ResizeToContents)


if __name__ == "__main__":
    app = QApplication()
    # app.setStyle("Fusion")
    ui = Explorer()
    ui.show()
    app.exec()
