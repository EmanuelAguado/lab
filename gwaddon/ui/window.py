from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QPushButton,
    QVBoxLayout,
    QApplication,
    QWidget,
)
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QColor, QPainter, QPalette, QIcon, QCursor, QPen
import win32con, win32gui
from ctypes.wintypes import POINT
import ctypes.wintypes
from ctypes import WinDLL, byref


# GLOBALS
class MINMAXINFO(ctypes.Structure):
    _fields_ = [
        ("ptReserved", POINT),
        ("ptMaxSize", POINT),
        ("ptMaxPosition", POINT),
        ("ptMinTrackSize", POINT),
        ("ptMaxTrackSize", POINT),
    ]


class MARGINS(ctypes.Structure):
    _fields_ = [
        ("cxLeftWidth", ctypes.c_int),
        ("cxRightWidth", ctypes.c_int),
        ("cyTopHeight", ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
    ]


class MainWindow(QFrame):
    BorderWidth = 0  # 10

    def __init__(self, widget=None, parent=None):
        super().__init__(parent)
        self.setObjectName("MainWindow")
        self.cursor = QCursor()
        self.createHeader()
        self.create_widgets()
        self.create_layout()
        # self.addLayout()
        self.create_style()
        self.widget = widget
        if self.widget:
            self.addWidget(self.widget)

    def paintEvent(self, event=None):
        painter = QPainter(self)
        painter.setOpacity(0.004)
        painter.setBrush(Qt.black)
        painter.setPen(QPen(Qt.black))
        painter.drawRect(self.rect())
        painter.setOpacity(100)
        painter.setBrush(QColor(10, 10, 10))  # QPalette().color(QPalette.Base))
        painter.setPen(QColor(10, 10, 10))  # QPen(QPalette().color(QPalette.Base)))
        painter.drawRect(
            QRect(
                self.BorderWidth,
                self.BorderWidth,
                self.width() - ((self.BorderWidth * 2) + 1),
                24,
            )
        )

        return super().paintEvent(event)

    def createHeader(self):
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(0)
        self.header_layout.setContentsMargins(0, 0, 0, 0)

        self.title = QLabel("Momfind")
        self.title.setStyleSheet("*{margin-left:10px}")
        self.spacer = QSpacerItem(5, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.title.setMinimumHeight(24)
        self.title.setMaximumHeight(24)

        self.bminimize = QPushButton()
        self.bminimize.setIcon(QIcon("ui/resources/img/minimize.png"))
        # self.bminimize.setAnimation(150,QColor(10,10,10),QPalette().color(QPalette.AlternateBase).name())
        self.bminimize.setMinimumSize(30, 24)
        self.bminimize.setMaximumSize(30, 24)

        self.bmaximize = QPushButton()
        self.bmaximize.setIcon(QIcon("ui/resources/img/maximize.png"))
        # self.bmaximize.setAnimation(150,QColor(10,10,10),QPalette().color(QPalette.AlternateBase).name())
        self.bmaximize.setMinimumSize(30, 24)
        self.bmaximize.setMaximumSize(30, 24)

        self.bclose = QPushButton()
        # self.bclose.setAnimation(150,QColor(10,10,10),"#CA3433")
        self.bclose.setIcon(QIcon("ui/resources/img/close.png"))
        self.bclose.setMinimumSize(30, 24)
        self.bclose.setMaximumSize(30, 24)

        self.header_layout.addWidget(self.title)
        self.header_layout.addItem(self.spacer)
        self.header_layout.addWidget(self.bminimize)
        self.header_layout.addWidget(self.bmaximize)
        self.header_layout.addWidget(self.bclose)

        self.bminimize.clicked.connect(lambda: self.showMinimized())
        self.bmaximize.clicked.connect(lambda: self.showMaximized())
        self.bclose.clicked.connect(lambda: self.close())

    def create_widgets(self):
        self.main_layout = QVBoxLayout(self)
        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")
        self.central_layout = QVBoxLayout(self.central_widget)

    def create_layout(self):
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.central_widget)

    def create_style(self):
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumSize(QSize(720, 512))
        self._rect = QApplication.instance().primaryScreen().availableGeometry()
        self.resize(800, 600)
        self.setWindowFlags(
            Qt.Window
            | Qt.FramelessWindowHint
            | Qt.WindowSystemMenuHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )
        style = win32gui.GetWindowLong(int(self.winId()), win32con.GWL_STYLE)
        win32gui.SetWindowLong(
            int(self.winId()), win32con.GWL_STYLE, style | win32con.WS_THICKFRAME
        )

        self.main_layout.setContentsMargins(
            self.BorderWidth, self.BorderWidth, self.BorderWidth, self.BorderWidth
        )
        self.main_layout.setSpacing(0)

        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        self.central_widget.setStyleSheet(
            "#central_widget{background-color:palette(mid)}"
        )
        self.setShadow()

    def addWidget(self, widget):
        self.widget = widget
        self.central_layout.addWidget(self.widget)

    def setShadow(self):
        WinDLL("dwmapi").DwmExtendFrameIntoClientArea(
            int(self.winId()), byref(MARGINS(-1, -1, -1, -1))
        )
        print("SHADOW")

    def nativeEvent(self, eventType, message):
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            pos = self.mapFromGlobal(self.cursor.pos())
            x = pos.x()
            y = pos.y()
            if msg.message == win32con.WM_NCCALCSIZE:
                return True, 0

            elif self.childAt(x, y) != None:
                return super().nativeEvent(eventType, message)

            elif msg.message == win32con.WM_GETMINMAXINFO:
                info = ctypes.cast(msg.lParam, ctypes.POINTER(MINMAXINFO)).contents
                info.ptMaxSize.x = self._rect.width()
                info.ptMaxSize.y = self._rect.height()
                info.ptMaxPosition.x, info.ptMaxPosition.y = 0, 0

            elif msg.message == win32con.WM_NCHITTEST:
                w, h = self.width(), self.height()
                lx = x < self.BorderWidth
                rx = x > w - self.BorderWidth
                ty = y < self.BorderWidth
                by = y > h - self.BorderWidth

                if lx and ty:
                    return True, win32con.HTTOPLEFT
                elif rx and by:
                    return True, win32con.HTBOTTOMRIGHT
                elif rx and ty:
                    return True, win32con.HTTOPRIGHT
                elif lx and by:
                    return True, win32con.HTBOTTOMLEFT
                elif ty:
                    return True, win32con.HTTOP
                elif by:
                    return True, win32con.HTBOTTOM
                elif lx:
                    return True, win32con.HTLEFT
                elif rx:
                    return True, win32con.HTRIGHT

                return True, win32con.HTCAPTION
            return super().nativeEvent(eventType, message)

    def closeEvent(self, event):
        try:
            self.widget.close()
        except:
            pass
        super().closeEvent(event)


if __name__ == "__main__":

    import sys

    app = QApplication()
    # app.setStyle("Fusion")

    main_ui = MainWindow()
    main_ui.show()
    print("SHOW")
    app.exec()
