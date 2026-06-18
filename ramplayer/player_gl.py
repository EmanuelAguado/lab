from threading import Thread
import time
from ffmpeg_utils import FFMPEGInfo, FFMPEGPlayer
from sys import argv, path as spath, platform
from os import fspath, environ
from pathlib import Path
from logging import getLogger, DEBUG, basicConfig

logger = getLogger(__name__)
basicConfig(level=DEBUG)

try:
    from PySide6.QtCore import (
        Qt,
        QPoint,
        QSize,
        QTimer,
        QRect,
        QRectF,
        Signal,
        QObject,
        QThread,
        QUrl,
    )
    from PySide6.QtGui import (
        QPainter,
        QPalette,
        QColor,
        QShortcut,
        QPixmap,
        QKeySequence,
        QImage,
        QFont,
        QMouseEvent,
    )
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink
    from PySide6.QtMultimediaWidgets import QVideoWidget
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
    from PySide6.QtWidgets import (
        QApplication,
        QPushButton,
        QHBoxLayout,
        QVBoxLayout,
        QWidget,
        QLabel,
        QSizePolicy,
        QSlider,
        QSpacerItem,
        QMainWindow,
    )

    pyside_version = 6
    QMouseEvent.pos = QMouseEvent.position
except:
    from PySide2.QtCore import QTimer, Qt, QSize, QRect, QPoint, QRectF, Signal, QObject, QThread  # type: ignore
    from PySide2.QtGui import (  # type: ignore
        QPainter,
        QPalette,
        QColor,
        QPixmap,
        QKeySequence,
        QFont,
        QMouseEvent,
        QImage,
    )
    from PySide2.QtMultimedia import QMediaPlayer, QMediaContent, QVideoProbe, QMediaPlaylist  # type: ignore
    from PySide2.QtMultimediaWidgets import QVideoWidget  # type: ignore
    from PySide2.QtWidgets import (  # type: ignore
        QApplication,
        QPushButton,
        QHBoxLayout,
        QVBoxLayout,
        QWidget,
        QLabel,
        QSizePolicy,
        QSlider,
        QSpacerItem,
        QMainWindow,
        QShortcut,
        QOpenGLWidget,
    )

    pyside_version = 2

spath.append(fspath(Path(__file__).parent.parent))
from player_utils import DefaultIcons

VIDEO_A = "C:/Users/emaag/Downloads/test.mp4"
VIDEO_B = "C:/Users/emaag/Downloads/test_inverted.mp4"
DEBUG_FPS = True


def thread(function):
    """Decorator that calls the function within a separate thread"""

    def wrapper(*args, **kwargs):
        worker = Thread(target=function, args=args, kwargs=kwargs)
        worker.start()

        return kwargs

    return wrapper


# def thread(function):
#     """Decorator that calls the function within a separate thread"""
#     def wrapper(ins, *args, **kwargs):
#         class Thread(QThread):
#             def start(self, function, *args, **kwargs):
#                 self.function = lambda: function(*args, **kwargs)
#                 return super().start()

#             def run(self):
#                 self.function()

#         ins.thread = Thread()
#         ins.thread.start(function, ins, *args, **kwargs)

#         return kwargs

#     return wrapper


class FrameThumbnail:
    def __init__(self, color, player, thumbnail=False):
        self._color = color
        self.player = player
        self.frame_number = 0
        self.real_frame_number = 0
        self.thumbnail = thumbnail
        self.rect = QRectF()
        self.is_cached = False
        self._width = 0

    def paint(self, painter):
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._color)
        painter.drawRect(self.rect)
        font_px = 8
        x, y, width, height = self.rect.getRect()
        if not self.thumbnail:
            pop_width = font_px * (len(str(self.frame_number)) + 2)
            pop_height = font_px * 3
            pop_x = max(
                0,
                min(
                    (x + (width / 2)) - (pop_width / 2), self.player.width() - pop_width
                ),
            )
            pop_y = y - pop_height - 5
            pop_frame = QRectF(pop_x, pop_y, pop_width, pop_height)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("black"))
            painter.drawRect(pop_frame)
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", font_px, QFont.Bold))
            painter.drawText(pop_frame, Qt.AlignCenter, str(self.frame_number))
        else:
            pop_width = 120
            pop_height = font_px * 3
            pop_x = max(
                0,
                min(
                    (x + (width / 2)) - (pop_width / 2), self.player.width() - pop_width
                ),
            )
            pop_y = y - pop_height - 5
            pop_frame = QRectF(pop_x, pop_y, pop_width, pop_height)
            pop_thumbnail_width = 120
            pop_thumbnail_height = 80
            pop_thumbnail_x = pop_x
            pop_thumbnail_y = pop_y - pop_thumbnail_height
            pop_thumbnail = QRectF(
                pop_thumbnail_x,
                pop_thumbnail_y,
                pop_thumbnail_width,
                pop_thumbnail_height,
            )
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("black"))
            painter.drawRect(pop_frame)
            painter.drawRect(pop_thumbnail)
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", font_px, QFont.Bold))
            painter.drawText(pop_frame, Qt.AlignCenter, str(self.frame_number))
            if self.player.media.ff_video.metadata.total_frames >= self.frame_number:
                frame = self.player.media.ff_video.cache.frames.get(
                    self.real_frame_number
                )
                if not frame:
                    return
                painter.drawPixmap(
                    pop_thumbnail_x,
                    pop_thumbnail_y,
                    pop_thumbnail_width,
                    pop_thumbnail_height,
                    QPixmap.fromImage(
                        QImage(
                            frame,
                            self.player.media.ff_video.metadata.width,
                            self.player.media.ff_video.metadata.height,
                            QImage.Format_RGB888,
                        )
                    ),
                )


class Frame:
    def __init__(self, frame_number):
        self.frame_number = frame_number
        self.rect = QRectF()
        self.is_cached = False
        self._width = 0

    def paint(self, painter):
        painter.setPen(Qt.NoPen)
        if self.is_cached:
            painter.setBrush(QColor("yellow"))
        else:
            painter.setBrush(QColor(50, 50, 50))
        painter.drawRect(self.rect)


class TimeLine:
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.selected_frame_item = FrameThumbnail(QColor("blue"), self.player)
        self.hovered_frame_item = FrameThumbnail(QColor("grey"), self.player, True)
        self.is_frame_selected = False
        self.frame_selected = None
        self.frame_hovered = None
        self.frames = []
        self.cache_frames = []
        self.no_cache_frames = []
        self.cache_frames_data = dict()
        self.no_cache_frames_data = dict()
        self.start_range = 0

    def get_frame_at_position(self, pos):
        for frame in self.frames:
            if frame.rect.contains(pos):
                return frame
        return None

    def on_select_frame(self, frame):
        self.is_frame_selected = True
        self.set_selected_frame(frame)

    def on_hover_frame(self, frame):
        self.frame_hovered = self.return_frame(frame)
        self.hovered_frame_item.frame_number = frame
        self.hovered_frame_item.real_frame_number = frame - self.start_range
        self.hovered_frame_item.rect = QRectF(self.frame_hovered.rect)

    def set_cached_frame(self, frame):
        frame_s = frame
        frame = self.return_frame(frame + self.start_range)
        if frame:
            frame.is_cached = True
            self.cache_frames_data[frame.frame_number] = frame.rect
            self.no_cache_frames_data.pop(frame.frame_number, None)
            self.cache_frames = list(self.cache_frames_data.values())
            self.no_cache_frames = list(self.no_cache_frames_data.values())

    def set_selected_frame(self, frame):
        self.frame_selected = self.return_frame(frame)
        self.selected_frame_item.frame_number = frame
        self.selected_frame_item.real_frame_number = frame - self.start_range
        self.selected_frame_item.rect = QRectF(self.frame_selected.rect)

    def set_flush_frame(self, frame):
        frame = self.return_frame(frame + self.start_range)
        if frame:
            frame.is_cached = False
            self.no_cache_frames_data[frame.frame_number] = frame.rect
            self.cache_frames_data.pop(frame.frame_number, None)
            self.no_cache_frames = list(self.no_cache_frames_data.values())
            self.cache_frames = list(self.cache_frames_data.values())

    def set_range(self, start, duration):
        self.start_range = start
        self.end_range = duration - 1 + self.start_range
        self.frames = []
        self.cache_frames = []
        self.no_cache_frames = []
        self.cache_frames_data = dict()
        self.no_cache_frames_data = dict()
        for idx, n in enumerate(range(self.start_range, self.end_range + 1)):
            frame = Frame(n)
            self.frames.append(frame)
            self.no_cache_frames_data[frame.frame_number] = frame.rect
            self.no_cache_frames.append(frame.rect)
        self.no_cache_frames = list(self.no_cache_frames_data.values())

        self.on_hover_frame(self.frames[0].frame_number)
        self.on_select_frame(self.frames[0].frame_number)
        self.is_frame_selected = False
        self.frame_hovered = False

    def return_frame(self, frame):
        real_frame = frame - self.start_range
        if real_frame < len(self.frames):
            return self.frames[real_frame]
        return None

    def update(self, painter):
        painter.setPen(Qt.NoPen)
        if self.no_cache_frames:
            painter.setBrush(QColor(20, 20, 20))
            painter.drawRects(self.no_cache_frames)
        if self.cache_frames:
            painter.setBrush(QColor("yellow"))
            painter.drawRects(self.cache_frames)
        self.update_hover(painter)
        self.update_select(painter)

    def update_hover(self, painter):
        if self.frame_hovered:
            self.hovered_frame_item.paint(painter)

    def update_select(self, painter):
        if self.selected_frame_item.rect.width() < 4:
            self.selected_frame_item.rect.setWidth(4)
        self.selected_frame_item.paint(painter)


class Crop:
    def __init__(self):
        self.rect = QRect()
        self._hover = False
        self._selected = False
        self.position = 0
        self.position_screen = 0

    def paint(self, painter):
        painter.setPen(Qt.NoPen)
        if self._selected:
            painter.setBrush(QColor("blue"))
        elif self._hover:
            painter.setBrush(QColor("white"))
        else:
            painter.setBrush(QColor("grey"))
        painter.drawRect(self.rect)


class Screen:
    def __init__(self, video=None, player=None):
        super().__init__()
        self.video = video
        self.player = player
        self.frame_size = None
        self.create_crops()

    def create_crops(self):
        self.crop_right = Crop()
        self.crop_right.position = 1
        self.crop_right.position_screen = 1
        self.crop_left = Crop()
        self.crop_left.position = 0
        self.crop_left.position_screen = 0

    def update_texture(self, frame, painter):
        aspect_ratio = self.video.metadata.width / self.video.metadata.height
        new_width = int(self.player.width())
        new_height = int(new_width / aspect_ratio)

        max_height = int(self.player.height()) - self.player.timeline_size
        if new_height > max_height:
            new_height = max_height
            new_width = int(new_height * aspect_ratio)

        x_offset = (self.player.width() - new_width) // 2
        y_offset = (
            (self.player.height() - self.player.timeline_size) - new_height
        ) // 2

        crop_left = self.crop_left.position_screen
        crop_right = self.crop_right.position_screen
        f_x = x_offset + (new_width * crop_left)
        c_x = self.video.metadata.width * crop_left
        f_width = new_width * (crop_right - crop_left)
        c_width = self.video.metadata.width * (crop_right - crop_left)
        if frame == -1:
            frame = 0
        if self.video.cache.frames.get(frame):
            self.todopx = {
                frame: QPixmap(
                    QImage(
                        self.video.cache.frames[frame],
                        self.video.metadata.width,
                        self.video.metadata.height,
                        QImage.Format_RGB888,
                    )
                )
            }
            painter.drawPixmap(
                f_x,
                y_offset,
                f_width,
                new_height,
                self.todopx[frame],
                c_x,
                0,
                c_width,
                self.video.metadata.height,
            )

    def update_crop(self, painter):
        width = self.player.width() - 5
        height = self.player.height()

        crop_right_pos = self.crop_right.position * width
        crop_left_pos = self.crop_left.position * width

        self.crop_right.rect = QRect(
            crop_right_pos, 0, 5, height - self.player.timeline_size
        )
        self.crop_right.paint(painter)

        self.crop_left.rect = QRect(
            crop_left_pos, 0, 5, height - self.player.timeline_size
        )
        self.crop_left.paint(painter)


class Media(QObject):
    on_frame_change = Signal()
    on_finish = Signal(object)
    on_set_source = Signal(object)

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.ff_video = None
        self.on_set_source.connect(self.set_source)
        self.bufferring = False
        self.reset()

    def reset(self):
        if pyside_version == 2:
            self.media = QMediaPlayer()
            self.video_widget = QVideoWidget()
            self.media.setVideoOutput(self.video_widget)
            self.playlist = QMediaPlaylist(self.media)
            self.media.setPlaylist(self.playlist)
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
            probe = QVideoProbe(self.media)
            probe.videoFrameProbed.connect(self.video_frame)
            probe.setSource(self)
            self.media.stateChanged.connect(self.on_finish.emit)
        else:
            self.media = QMediaPlayer()
            self.media.setLoops(QMediaPlayer.Infinite)
            self.audio = QAudioOutput()
            self.video_sink = QVideoSink()
            self.media.setAudioOutput(self.audio)
            self.media.setVideoOutput(self.video_sink)
            self.video_sink.videoFrameChanged.connect(self.video_frame)

    def play(self):
        # ERROR: play pause coloca el video donde no toca
        self.media.setPosition(
            int(
                (
                    (self.player.player.current_frame + 2)
                    / self.ff_video.metadata.frame_rate
                )
                * 1000
            )
        )
        if not self.ff_video.cache.full:
            self.player.player.playing_decode()
        self.media.play()

    def set_source(self, ff_video):
        self.ff_video = ff_video
        video_path = ff_video.video_path.replace("\\", "/")
        if pyside_version == 2:
            self.playlist.addMedia(QMediaContent(video_path))
        else:
            self.media.setSource(QUrl(video_path))

    @thread
    def video_frame(self, frame):
        while not self.ff_video.cache.frames.get(
            self.player.possible_next_frame()
        ) and self.player.player.state in [FFMPEGInfo.play, FFMPEGInfo.buffering]:
            if self.player.player.state == FFMPEGInfo.play:
                self.player.on_buffering_signal.emit()
            time.sleep(0.00001)
        if self.player.player.state in [FFMPEGInfo.play, FFMPEGInfo.buffering]:
            if self.player.player.state == FFMPEGInfo.buffering:
                self.player.on_play_signal.emit()
            self.on_frame_change.emit()


class GLPlayer(QOpenGLWidget):
    on_state_changed = Signal(object)
    on_fps_changed = Signal(int or float)
    on_total_frames_change = Signal(int)
    on_play_signal = Signal()
    on_pause_signal = Signal()
    on_stop_signal = Signal()
    on_buffering_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.initialize = False
        self.screen_status = True
        self.timeline_size = 15
        self.debug_fps_start = 0
        self.timer_screen = QTimer()
        self.timer_screen.timeout.connect(self.update)
        self.offset_screen_x = 1
        self.min_x_screen = 0
        self.max_x_screen = 0
        self.timeline = TimeLine(self)
        self.player = FFMPEGPlayer()
        self.media = Media(self)
        self.media.on_frame_change.connect(self.refresh_frame)
        self.on_play_signal.connect(self.on_play)
        self.on_pause_signal.connect(self.on_pause)
        self.on_stop_signal.connect(self.on_stop)
        self.on_buffering_signal.connect(self.on_buffering)

        self.screens = dict()

    def set_video(self, video: str, screen_id: int = 0):
        logger.debug(f"reset Media: {video} | Screen {screen_id}")
        self.media.reset()
        self.load_video(video)

    @thread
    def load_video(self, video: str, screen_id: int = 0):
        ff_video = self.player.add_video(video)
        logger.debug(f"[{ff_video}] create screen")
        self.screens[screen_id] = Screen(ff_video, self)
        logger.debug(f"ff_video: {ff_video}")
        # if screen_id == 0:
        logger.debug(f"[{ff_video}] Setting cache connections")
        ff_video.cache.signal_cache_frame = self.timeline.set_cached_frame
        ff_video.cache.signal_flush_frame = self.timeline.set_flush_frame

        logger.debug(f"[{ff_video}] Setting media source")
        self.media.set_source(ff_video)
        logger.debug(f"[{ff_video}] Setting timeline range")
        self.timeline.set_range(1, ff_video.metadata.total_frames)
        logger.debug(f"[{ff_video}] Setting fps")
        self.on_fps_changed.emit(ff_video.metadata.frame_rate)
        logger.debug(f"[{ff_video}] Setting framerate")
        self.on_total_frames_change.emit(ff_video.metadata.total_frames)
        logger.debug(f"[{ff_video}]  update aspect ratio")
        self.update_aspect_ratio()
        logger.debug(f"[{ff_video}] initialize decode")
        ff_video.frame(0)

        self.player.initialize_decode()
        # self.player.current_frame = -1

    def remove_video(self, video_id):
        self.media.ff_video = None

    def initializeGL(self):
        self.initialize = True
        self.timer_screen.start()

    def paintGL(self):
        if DEBUG_FPS:
            self.debug_fps_end = time.perf_counter()
            time_result = round(1 / (self.debug_fps_end - self.debug_fps_start))
            self.debug_fps_start = time.perf_counter()
        painter = QPainter(self)
        for screen in self.screens.values():
            if screen.video:
                screen.update_texture(self.player.current_frame, painter)

        # for screen in self.screens.values():
        #     screen.update_crop(painter)

        self.timeline.update(painter)
        if DEBUG_FPS:
            painter.setPen(Qt.green)
            painter.setFont(QFont("Arial", 20, QFont.Bold))
            painter.drawText(
                QRect(10, 10, self.width(), self.height()),
                Qt.AlignLeft,
                f"{time_result}FPS",
            )

        painter.end()

    def resizeGL(self, width, height):
        if self.media.ff_video:
            self.update_aspect_ratio()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.LeftButton:
            return
        try:
            event_position = event.pos().toPoint()
        except:
            event_position = event.pos()

        list_screen = list(self.screens.values())
        list_screen.reverse()
        for screen in list_screen:
            for crop in [
                screen.crop_right,
                screen.crop_left,
                # screen.crop_top,
                # screen.crop_bottom,
            ]:
                if not crop.rect.contains(event_position):
                    crop._selected = False
                    continue
                crop._selected = True
                break
            else:
                continue
            break

        frame = self.timeline.get_frame_at_position(event_position)
        if not frame:
            return
        self.on_pause()
        self.timeline.on_select_frame(frame.frame_number)
        self.player.current_frame = frame.frame_number - self.timeline.start_range
        # if not self.media.ff_video.cache.frames.get(self.player.current_frame):
        #     self.on_pause_decode()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        list_screen = list(self.screens.values())
        list_screen.reverse()
        for screen in list_screen:
            screen.crop_right._selected = False
            screen.crop_left._selected = False
            # screen.crop_top._selected = False
            # screen.crop_bottom._selected = False
        self.timeline.is_frame_selected = False
        return super().mouseReleaseEvent(event)

    def leaveEvent(self, event: QMouseEvent) -> None:
        list_screen = list(self.screens.values())
        list_screen.reverse()
        for screen in list_screen:
            screen.crop_right._selected = False
            screen.crop_left._selected = False
            # screen.crop_top._selected = False
            # screen.crop_bottom._selected = False
        self.timeline.is_frame_selected = False
        self.timeline.frame_hovered = False
        return super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        event_position = event.pos().x()
        list_screen = list(self.screens.values())
        list_screen.reverse()
        if not self.timeline.is_frame_selected:
            for screen in list_screen:
                for crop in [
                    screen.crop_right,
                    screen.crop_left,
                    # screen.crop_top,
                    # screen.crop_bottom,
                ]:
                    if crop._selected:
                        range_min = self.min_x_screen / self.width()
                        range_max = self.max_x_screen / self.width()
                        crop.position = max(
                            range_min,
                            min(event.pos().x() / self.width(), range_max),
                        )
                        crop.position_screen = max(
                            0,
                            min(
                                (crop.position - range_min) / (range_max - range_min), 1
                            ),
                        )
                        return
                    if pyside_version == 6:
                        crop._hover = crop.rect.contains(event.pos().toPoint())
                    else:
                        crop._hover = crop.rect.contains(event.pos())
            frame = self.timeline.get_frame_at_position(
                QPoint(event_position, event.pos().y())
            )
            if frame:
                self.timeline.on_hover_frame(frame.frame_number)
                return
            self.timeline.frame_hovered = None
        else:
            frame = self.timeline.get_frame_at_position(
                QPoint(event_position, self.height() - self.timeline_size)
            )
            if not frame:
                return
            self.timeline.on_select_frame(frame.frame_number)
            self.player.current_frame = frame.frame_number - self.timeline.start_range
            self.timeline.frame_hovered = None

    def update_aspect_ratio(self):
        width = self.width()
        height = self.height()

        self.aspect_ratio = width / (height - self.timeline_size)
        video_aspect_ratio = (
            self.media.ff_video.metadata.width / self.media.ff_video.metadata.height
        )

        if self.aspect_ratio > video_aspect_ratio:
            self.offset_screen_x = video_aspect_ratio / self.aspect_ratio
            self.min_x_screen = round(width - (width * self.offset_screen_x), 10) / 2
            self.max_x_screen = width - self.min_x_screen
        else:
            self.offset_screen_x = 1
            self.min_x_screen = 0
            self.max_x_screen = width
        if self.aspect_ratio > video_aspect_ratio:
            list_screen = list(self.screens.values())
            list_screen.reverse()
            for screen in list_screen:
                range_min = self.min_x_screen / width
                range_max = self.max_x_screen / width
                for crop in [
                    screen.crop_right,
                    screen.crop_left,
                ]:
                    crop.position = range_min + (
                        crop.position_screen * (range_max - range_min)
                    )

        frame_width = width / len(self.timeline.frames)
        for i, frame in enumerate(self.timeline.frames):
            frame.rect.setRect(
                i * frame_width,
                height - self.timeline_size,
                frame_width,
                self.timeline_size,
            )
            frame._width = frame_width
        if self.timeline.frame_selected:
            self.timeline.selected_frame_item.rect = QRectF(
                self.timeline.frame_selected.rect
            )
        if self.timeline.frame_hovered:
            self.timeline.hovered_frame_item.rect = QRectF(
                self.timeline.frame_hovered.rect
            )

    def update_screen(self):
        # TODO: Crear un sistema para que la pantalla no este actualizandose si no tiene nada que actualizar
        if self.screen_status:
            self.update()

    def possible_next_frame(self):
        if self.player.current_frame >= self.media.ff_video.metadata.total_frames - 1:
            return 0
        else:
            return self.player.current_frame + 1

    def refresh_frame(self):
        if not self.media.ff_video:
            return
        if self.player.state == FFMPEGInfo.play:
            self.player.current_frame = self.possible_next_frame()
            self.timeline.set_selected_frame(
                self.player.current_frame + self.timeline.start_range
            )

    def on_play(self):
        if self.player.state == FFMPEGInfo.play:
            return
        print("[STATE] play")
        if self.media.ff_video:
            if self.player.state == FFMPEGInfo.buffering:
                self.media.media.play()
            else:
                self.media.play()
            self.player.state = FFMPEGInfo.play
        self.on_state_changed.emit(self.player.state)

    def on_pause(self):
        if self.player.state == FFMPEGInfo.pause:
            return
        print("[STATE] pause")
        self.player.state = FFMPEGInfo.pause
        if self.media.ff_video:
            self.player.pausing_decode()
            self.media.media.pause()
        self.on_state_changed.emit(self.player.state)
        # self.player.pausing_decode()

    def on_buffering(self):
        if self.player.state == FFMPEGInfo.buffering:
            return
        print("[STATE] buffer")
        self.player.state = FFMPEGInfo.buffering
        if self.media.ff_video:
            self.media.media.pause()

            # self.player.playing_decode()

    def on_stop(self):
        self.player.state = FFMPEGInfo.stop
        self.on_state_changed.emit(self.player.state)

    def next_frame(self):
        if not self.media.ff_video:
            return
        if self.player.state == FFMPEGInfo.play:
            self.on_pause()
        if self.player.current_frame >= self.media.ff_video.metadata.total_frames - 1:
            self.player.current_frame = 0
        else:
            self.player.current_frame += 1
        # if not self.media.ff_video.cache.frames.get(self.player.current_frame):
        #     self.on_pause_decode()
        self.timeline.set_selected_frame(
            self.player.current_frame + self.timeline.start_range
        )

    def previous_frame(self):
        if not self.media.ff_video:
            return
        if self.player.state == FFMPEGInfo.play:
            self.on_pause()
        if self.player.current_frame == 0:
            self.player.current_frame = self.media.ff_video.metadata.total_frames - 1
        else:
            self.player.current_frame -= 1
        # if not self.media.ff_video.cache.frames.get(self.player.current_frame):
        #     self.on_pause_decode()
        self.timeline.set_selected_frame(
            self.player.current_frame + self.timeline.start_range
        )

    # @thread
    # def on_pause_decode(self):
    #     self.player.pausing_decode()


class PlayerWidget(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        print("Initialize UI")
        self.create_widgets()
        print("Creating UI connections")
        self.create_connections()
        self.create_shortcut()
        print("Creating UI connections success")
        self.setAcceptDrops(True)
        self.resize(800, 600)
        print("Initialize UI sucess")

    def create_widgets(self):
        self._main_widget = QWidget(self)
        self.setCentralWidget(self._main_widget)
        self._main_layout = QVBoxLayout(self._main_widget)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        self._player_view = GLPlayer()
        self._main_layout.addWidget(self._player_view)
        self.create_video_buttons()

    def create_video_buttons(self):
        self._fps_label = QLabel("---")
        self._fps_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self._fps_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._total_frames_label = QLabel("---")
        self._total_frames_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self._total_frames_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        string_fps = QLabel(" fps ")
        string_frames = QLabel(" frames")
        string_fps.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        string_frames.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.setContentsMargins(5, 0, 5, 0)
        self._buttons_layout.setSpacing(0)
        self._play_button = QPushButton(DefaultIcons.PLAY, "")
        self._previous_frame_button = QPushButton(QPixmap("arrow_left.png"), "")
        self._next_frame_button = QPushButton(QPixmap("arrow_right.png"), "")
        self._volume_button = QSlider(Qt.Horizontal)
        self._volume_button.setMaximum(100)
        self._volume_button.setProperty("value", 100)
        self._volume_button.setMaximumSize(100, 20)
        self._config_button = QPushButton(QPixmap("settings.gif"), "")
        self._config_button.setIconSize(QSize(20, 20))

        self._buttons_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        self._buttons_layout.addWidget(self._fps_label)
        self._buttons_layout.addWidget(string_fps)
        self._buttons_layout.addWidget(self._previous_frame_button)
        self._buttons_layout.addWidget(self._play_button)
        self._buttons_layout.addWidget(self._next_frame_button)
        self._buttons_layout.addWidget(self._total_frames_label)
        self._buttons_layout.addWidget(string_frames)
        self._buttons_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        self._buttons_layout.addWidget(self._config_button)
        self._main_layout.addLayout(self._buttons_layout)

    def create_connections(self):
        self._next_frame_button.clicked.connect(self._player_view.next_frame)
        self._previous_frame_button.clicked.connect(self._player_view.previous_frame)
        self._play_button.clicked.connect(self.on_player_state_changed)
        self._player_view.on_fps_changed.connect(self.set_fps)
        self._player_view.on_total_frames_change.connect(self.set_total_frames)
        # self._player_view.on_play_signal.connect(lambda:self._play_button.setIcon(DefaultIcons.PAUSE))
        # self._player_view.on_pause_signal.connect(lambda:self._play_button.setIcon(DefaultIcons.PLAY))

    def create_shortcut(self):
        self.shortcut_play = QShortcut(
            QKeySequence(Qt.Key_Space), self, self.on_player_state_changed
        )
        self.shortcut_next_frame = QShortcut(
            QKeySequence(Qt.Key_Right), self, self._player_view.next_frame
        )
        self.shortcut_back_frame = QShortcut(
            QKeySequence(Qt.Key_Left), self, self._player_view.previous_frame
        )

    def on_player_state_changed(self) -> None:
        if not self._player_view.media.ff_video:
            return
        if self._player_view.player.state in [FFMPEGInfo.play, FFMPEGInfo.buffering]:
            self._play_button.setIcon(DefaultIcons.PLAY)
            self._player_view.on_pause()
        else:
            self._play_button.setIcon(DefaultIcons.PAUSE)
            self._player_view.on_play()

    def set_fps(self, value):
        self._fps_label.setText(str(value))

    def set_total_frames(self, value):
        self._total_frames_label.setText(f" {value}")


def style(app):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(35, 35, 35))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(10, 10, 10))
    palette.setColor(QPalette.AlternateBase, QColor(25, 25, 25))
    palette.setColor(QPalette.Light, QColor(20, 20, 20))
    palette.setColor(QPalette.Midlight, QColor(50, 50, 50))
    palette.setColor(QPalette.Dark, QColor(10, 10, 10))
    palette.setColor(QPalette.Mid, QColor(20, 20, 20))
    palette.setColor(QPalette.Shadow, QColor(1, 1, 1))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setStyleSheet(
        "QComboBox {background-color: palette(mid);border: none;text-align:center;font-weight: bold;}"
        "QComboBox::drop-down {border: none;}"
        "QComboBox::down-arrow {image: url(./down.png);width: 8px;height: 8px;}"
        "QComboBox::editable, QComboBox::drop-down:editable {background: transparent;}"
        "QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }"
        "QPushButton, QToolButton { background-color: palette(dark);border:none;padding:5px}"
        "QPushButton:hover, QToolButton:hover {background-color:palette(mid);border:none;padding:5px;}"
        "QPushButton:checked, QToolButton:checked,QPushButton:pressed, QToolButton:pressed {background-color:palette(highlight)}"
    )
    app.setPalette(palette)


if __name__ == "__main__":
    environ["FFMPEG_BIN"] = "C:/Users/emaag/Downloads/ffmpeg/bin/ffmpeg.exe"
    environ["FFPROBE_BIN"] = "C:/Users/emaag/Downloads/ffmpeg/bin/ffprobe.exe"
    app = QApplication.instance()
    style(app)
    window = PlayerWidget()
    # VIDEO_A = "C:/Users/emaag/Downloads/gri_109_040_080-01_anim_rfn_004.mov"
    # VIDEO_A = "C:/Users/emaag/Downloads/test.mp4"
    # VIDEO_A = r"C:\Users\emaag\Downloads\gri_108_030_140_01_comp_com_002.mp4"
    # VIDEO_A = r"C:\Users\emaag\Downloads\gri_101_100_050-01_anim_rfn_002.mov"
    # VIDEO_B = "C:/Users/emaag/Downloads/test.mp4"
    window._player_view.set_video(VIDEO_A)
    window.show()
    app.exec()