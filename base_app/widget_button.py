from PySide6.QtWidgets import (
    QPushButton,
    QToolButton,
    QLabel,
)
from PySide6.QtCore import (
    QVariantAnimation,
    QAbstractAnimation,
    Signal,
    Qt,
)
from PySide6.QtGui import (
    QPalette,
    QColor,
    QPixmap,
    QPainter,
    QPainterPath,
)


class APushButton(QPushButton):
    def __init__(
        self, title="", time=None, valueA=None, valueB=None, radius=0, parent=None
    ):
        super().__init__(parent)
        self._animation = None
        self._radius = radius
        self.setText(title)
        if not time and not valueA and not valueB:
            self.setAnimation(
                250,
                QPalette().color(QPalette.Dark).name(),
                QPalette().color(QPalette.Light).name(),
            )
        else:
            self.setAnimation(time, valueA, valueB)

    def setAnimation(self, time=0, valueA="", valueB=""):
        self._animation = QVariantAnimation(self)
        self._animation.valueChanged.connect(self._animate)
        self._animation.setStartValue(QColor(valueA))
        self._animation.setEndValue(QColor(valueB))
        self._animation.setDuration(time)

    def _animate(self, value):

        style = "*{{background-color: {value};border:None;padding:10px;border-radius:{radius}}}".format(
            value=value.name(), radius=self._radius
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
            "*{background-color: " + value.name() + ";border:None}"
            "*::menu-button {background-color: palette(Base)}"
            "*::menu-arrow {image: url(resources/img/arrowRight)} "
            "*::menu-button:hover {background-color: 2px palette(Highlight);border-left:2px solid palette(Base);}"
            "*:checked{background-color:palette(Highlight)}"
            "*::menu-arrow:open {image: url(resources/img/arrowDown)}"
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


class RoundButton(QLabel):
    clicked = Signal()

    def __init__(
        self,
        *args,
        text="",
        icon=None,
        background="palette(highlight)",
        size=[256, 256],
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._text = text
        self.background = background
        self._size = size
        self.setMaximumSize(self._size[0], self._size[1])
        self.setMinimumSize(self._size[0], self._size[1])
        self.radius = ((self._size[0] + self._size[1]) / 2) / 2

        self.active = True

        self.target = QPixmap(self.size())
        self.target.fill(Qt.transparent)

        self._icon = icon

        self.target = QPixmap(self.size())
        self.target.fill(Qt.transparent)

        p = QPixmap(self._icon).scaled(
            self._size[0],
            self._size[1],
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )
        self.painter = QPainter(self.target)
        self.painter.setRenderHint(QPainter.Antialiasing, True)
        # self.painter.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing, True)
        self.painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)

        self.painter.setClipPath(path)
        self.painter.drawPixmap(0, 0, p)
        self.setPixmap(self.target)

        self.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

    def setActive(self, status):

        self.active = status

        if not self.active:
            self.setStyleSheet(
                "background-color:palette(mid);border-radius:{}".format(self.radius)
            )
            self.setText("")
            self.setPixmap(QPixmap())
            p = QPixmap(self._icon).scaled(
                self._size[0],
                self._size[1],
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            self.painter.drawPixmap(0, 0, p)
            self.setPixmap(self.target)
            self.repaint()

    def setIcon(self, icon):
        self._icon = icon
        p = QPixmap(self._icon).scaled(
            self._size[0],
            self._size[1],
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )
        self.painter.drawPixmap(0, 0, p)
        self.setPixmap(QPixmap())
        self.setPixmap(self.target)
        self.repaint()

    def mousePressEvent(self, event):
        if self.active:
            self.clicked.emit()

    def enterEvent(self, event):

        if self.active:
            self.setStyleSheet(
                "background-color:{};border-radius:{}".format(
                    self.background, self.radius
                )
            )
            self.setText(self._text)
            super().enterEvent(event)

    def leaveEvent(self, event):

        self.setStyleSheet(
            "background-color:palette(mid);border-radius:{}".format(self.radius)
        )
        self.setText("")
        self.setPixmap(self.target)
        super().leaveEvent(event)

    def closeEvent(self, event):

        self.painter.end()
