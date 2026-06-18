# START OF STANDARD LIBRARY IMPORTS
from os import environ
from pprint import pprint
from subprocess import run, check_output, STDOUT, Popen, PIPE, DEVNULL
from sys import platform, getsizeof
from threading import Thread
import time

if platform == "win32":
    from subprocess import CREATE_NO_WINDOW
else:
    CREATE_NO_WINDOW = 0
from typing import Any, Dict, Union
from logging import getLogger

logger = getLogger(__name__)

import json
from math import floor
from pathlib import Path



# class FrameThumbnail: (player_qt) leer los fotogramas en paralelo y guardarlo a una resolucion pequeña, para que si hay frames que no han sido cacheados se puedan previsualizar
def thread(function):
    """Decorator that calls the function within a separate thread"""

    def wrapper(*args, **kwargs):
        worker = Thread(target=function, args=args, kwargs=kwargs)
        worker.start()

        return kwargs

    return wrapper


class FFMPEGPlayer:
    CACHE_LIMIT = 2048
    CACHE_SIZE = 0
    CACHE_SIZE_PER_FRAME = 0

    def __init__(self):
        self.info = FFMPEGInfo()
        self.videos = dict()
        self._id = -1
        self.current_frame = -1  # frame real, siempre va de 0 a num de frames - 1
        self.state = FFMPEGInfo.stop
        self.start_frame = 0
        self.end_frame = 0
        self.decoding_in_use = False
        self.stop_decoding = False
        self.playing_decode_in_use = False
        self.direction = "right"

    def add_video(self, video_path: Union[str, Path], concat: bool = False):
        self._id += 1
        self.videos[self._id] = FFMPEGVideo(video_path, self._id, self)

        if concat:
            self.videos[self._id].set_starting_frame(self.end_frame)
            self.end_frame += self.videos[self._id].metadata.total_frames
        else:
            self.end_frame = (
                self.videos[self._id].metadata.total_frames
                if self.videos[self._id].metadata.total_frames > self.end_frame
                else self.end_frame
            )
        print(f"[FFMPEGPlayer] add ffvideo: {self._id} | {video_path}")
        return self.videos[self._id]

    def frame(self, frame_number) -> Dict[int, bytes]:
        """Retorna el fotograma dado de todos los videos."""
        frames = dict()
        for _id, ffvideo in self.videos.items():
            frames[_id] = ffvideo.frame(frame_number)
        return frames

    def initialize_decode(self, frame_number: int = 0):
        self.stop_decoding = True
        while self.decoding_in_use:
            pass
        self.decoding_in_use = True
        self.stop_decoding = False

        frames_in_memory = self.CACHE_LIMIT / sum(
            [ffvideo.cache.frame_size_in_memory for ffvideo in self.videos.values()]
        )
        self.frames_paddin_left = floor(frames_in_memory * 0.3)
        self.frames_paddin_right = floor(frames_in_memory * 0.7)
        for current_frame_number in range(frame_number, self.end_frame):
            for ffvideo in self.videos.values():
                if self.stop_decoding:
                    self.decoding_in_use = False
                    return
                if (ffvideo.starting_frame <= current_frame_number) and (
                    current_frame_number
                    < (ffvideo.starting_frame + ffvideo.metadata.total_frames)
                ):
                    if (
                        self.CACHE_SIZE + ffvideo.cache.frame_size_in_memory
                        >= self.CACHE_LIMIT
                    ):
                        self.decoding_in_use = False
                        return
                    # print(
                    #     f"[FFMPEGPlayer-ffvideo {ffvideo.id}] decode: {current_frame_number}/{self.end_frame - 1}"
                    # )
                    ffvideo.frame(current_frame_number)
        self.decoding_in_use = False
        self.stop_decoding = False

    @thread
    def playing_decode(self):
        if list(self.videos.values())[0].cache.full:
            print("FULL")
            return
        print("[DECODE PLAY] Start")
        self.direction = "right"
        self.stop_decoding = True
        while self.decoding_in_use:
            time.sleep(0.00001)
            # return
        print("[DECODE PLAY] Starting")
        self.stop_decoding = False
        self.decoding_in_use = True
        last_frame = 0
        current_frame_number = self.current_frame
        while (
            self.state in [FFMPEGInfo.play, FFMPEGInfo.buffering]
            and not self.stop_decoding
        ):
            if self.state != FFMPEGInfo.buffering:
                if (
                    current_frame_number
                    not in range(
                        self.current_frame - self.frames_paddin_left,
                        self.current_frame + self.frames_paddin_right,
                    )
                    and last_frame == self.current_frame
                ):
                    time.sleep(0.0001)
                    continue

            last_frame = self.current_frame
            if (
                current_frame_number
                >= list(self.videos.values())[0].metadata.total_frames - 1
            ):
                current_frame_number = 0
            else:
                current_frame_number += 1
            self.decode_frame(current_frame_number)

        print("[DECODE PLAY] Finish")
        self.decoding_in_use = False
        self.stop_decoding = False

    @thread
    def pausing_decode(self):
        if list(self.videos.values())[0].cache.full:
            print("FULL")
            return
        print("[DECODE PAUSE] Start")
        self.stop_decoding = True
        while self.decoding_in_use:
            time.sleep(0.00001)
            pass
        print("[DECODE PAUSE] Starting")
        self.stop_decoding = False
        self.decoding_in_use = True
        ffvideo_0 = list(self.videos.values())[0]
        lock_cache_range = [0, 0]
        last_frame = 0
        done = False
        self.direction = "left"
        while self.state == FFMPEGInfo.pause and not self.stop_decoding:
            if (
                self.current_frame >= lock_cache_range[0]
                and self.current_frame <= lock_cache_range[1]
                and done
                and ffvideo_0.cache.frames.get(frame_number)
            ):
                time.sleep(0.001)
                continue
            self.direction = "right" if self.current_frame >= last_frame else "left"
            last_frame = self.current_frame
            if self.direction == "left":
                start = self.current_frame
                end = start + self.frames_paddin_left + self.frames_paddin_right + 1
            else:
                start = self.current_frame - self.frames_paddin_left
                end = self.current_frame + self.frames_paddin_right + 1

            if end >= ffvideo_0.metadata.total_frames - 1:
                end = ffvideo_0.metadata.total_frames
            # pending_cache = sorted(list(set(range(start,end)) - set(ffvideo_0.cache.frames_cached)))
            for frame_number in range(start, end):
                if self.stop_decoding or last_frame != self.current_frame:
                    lock_cache_range = [start, end - self.frames_paddin_right]
                    done = False
                    break
                self.decode_frame(frame_number)
                done = True
            lock_cache_range = [start, end - self.frames_paddin_right]
            time.sleep(0.001)

        print("[DECODE PAUSE] Finish")
        self.decoding_in_use = False
        self.stop_decoding = False

    def decode_frame(self, frame_number):
        for ffvideo in self.videos.values():
            if ffvideo.cache.frames.get(frame_number):
                continue
            ffvideo.frame(frame_number)


class FFMPEGVideo:
    def __init__(
        self,
        video_path: Union[str, Path],
        id: int,
        player: FFMPEGPlayer,
    ):
        self.id = id
        self.player = player
        self.video_path = video_path
        self.metadata = FFMPEGMetadata(self)
        self.decoder = FFMPEGDecoder(self)
        self.cache = FFMPEGCache(self)
        self.starting_frame = 0
        self.cache.initialize()

    def set_starting_frame(self, frame_number):
        self.starting_frame = frame_number

    def frame(self, frame_number):
        video_frame = self.cache.return_frame(frame_number - self.starting_frame)
        if video_frame is None:
            video_frame = self.decoder.decode(frame_number - self.starting_frame)
            # print(f"[VF] {frame_number - self.starting_frame} {len(str(video_frame))}")
            self.cache.add_frame(frame_number, video_frame)
        return video_frame


class FFMPEGCache:
    signal_cache_frame = None
    signal_flush_frame = None

    def __init__(self, video) -> None:
        super().__init__()
        self.video = video
        self.frames = dict()
        self.frames_cached = list()
        self.frame_size_in_memory = 0
        self.full = False

    def initialize(self):
        self.frames = {frame: None for frame in range(self.video.metadata.total_frames)}
        self.frames_cached = list()
        self.set_padding()

    def add_frame(self, frame_number, video_frame):
        if self.video.player.CACHE_LIMIT <= (
            self.video.player.CACHE_SIZE + self.frame_size_in_memory
        ):
            if not self.frames_cached:
                return

            # TODO: En vez de borrar el ultimo cacheado, serría mejor borrar el más lejano al current frame,
            # y saberr en que direccion se mueve
            # if self.video.player.direction == "left":
            #     remove_frame = list(
            #         set(self.frames_cached)
            #         - set(
            #             range(
            #                 self.video.player.current_frame,
            #                 self.video.player.current_frame
            #                 + self.video.player.frames_paddin_right
            #                 + self.video.player.frames_paddin_left,
            #             )
            #         )
            #     )
            # else:
            #     remove_frame = list(
            #         set(self.frames_cached)
            #         - set(
            #             range(
            #                 self.video.player.current_frame
            #                 - self.video.player.frames_paddin_left,
            #                 self.video.player.current_frame
            #                 + self.video.player.frames_paddin_right,
            #             )
            #         )
            #     )
            # if not remove_frame:
            #     return
            # lock = remove_frame[0]
            # self.flush_frame(lock)
            lock_frame = self.frames_cached[0]
            self.flush_frame(lock_frame)
        if self.frames.get(frame_number) is None:
            self.frames[frame_number] = video_frame
            self.emit_signal(self.signal_cache_frame, frame_number)
            self.frames_cached.append(frame_number)
            self.video.player.CACHE_SIZE += self.frame_size_in_memory
        self.full = len(self.frames_cached) == self.video.metadata.total_frames

    def flush_frame(self, frame_number):
        if self.frames.get(frame_number) is not None:
            self.frames[frame_number] = None
            self.frames_cached.remove(frame_number)
            self.video.player.CACHE_SIZE -= self.frame_size_in_memory
            self.emit_signal(self.signal_flush_frame, frame_number)

    def set_padding(self):
        if not self.frames_cached:
            self.video.frame(0)
        frame = self.frames[0]
        self.frame_size_in_memory = getsizeof(frame) / (1024 * 1024)
        self.clear_cache()
        self.video.decoder.set_frame(0)

    def clear_cache(self):
        for frame in self.frames_cached:
            self.flush_frame(frame)

    def return_frame(self, frame_number):
        return self.frames.get(frame_number)

    def emit_signal(self, signal, *args, **kwargs):
        if signal:
            signal(*args, **kwargs)


class FFMPEGInfo:
    play = 0
    pause = 1
    stop = 2
    buffering = 3

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        if hasattr(self, "initialized"):
            # TODO: find a cleaner way of checking whether app has been instantiated
            return
        super().__init__()
        self.initialized = True

        command = [
            environ.get("FFPROBE_BIN"),
            "-v",
            "error",
            "-show_pixel_formats",
            "-print_format",
            "json",
        ]
        output = check_output(command, stderr=STDOUT, text=True)
        self.data = json.loads(output)
        self.pix_fmts = dict()
        for pix_fmt in self.data.get("pixel_formats"):
            self.pix_fmts[pix_fmt.get("name")] = pix_fmt.get("nb_components")


class FFMPEGMetadata:
    def __init__(self, video: FFMPEGVideo) -> None:
        self.video = video
        command = [
            environ.get("FFPROBE_BIN"),
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-select_streams",
            "v:0",
            # "-show_format",
            "-show_streams",
            # "-show_packets",
            # "-show_frames",
            # "-show_programs",
            # "-show_chapters",
            # "-count_frames",
            self.video.video_path,
        ]

        output = check_output(command, stderr=STDOUT, text=True)
        self.data = json.loads(output)
        self.width = self.data["streams"][0].get("width")
        self.height = self.data["streams"][0].get("height")
        self.pix_fmt = self.data["streams"][0].get("pix_fmt")
        num, denom = self.data["streams"][0].get("r_frame_rate").split("/")
        self.frame_rate = float(num) / float(denom)
        try:
            self.total_frames = int(self.data["streams"][0].get("nb_frames"))
        except:
            self.total_frames = int(
                float(self.data["streams"][0].get("duration")) * self.frame_rate
            )


class FFMPEGDecoder:
    def __init__(self, video: FFMPEGVideo):
        self.video = video
        self.process = None
        self.frame = 0

    def start(self):
        if self.process is None:
            command = [
                environ.get("FFMPEG_BIN"),
                "-stream_loop",
                "-1",
                "-i",
                self.video.video_path,
                "-vf",
                f"select=gte(n\\,{self.frame})",
                # f"select=gte(n\\,{self.frame}),scale=192:108",
                "-vsync",
                "0",
                "-f",
                "image2pipe",
                "-vcodec",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-",
            ]
            self.process = Popen( command, stdout=PIPE, stderr=DEVNULL)

    def decode(self, frame_number=None):
        if frame_number and frame_number != self.frame:
            self.set_frame(frame_number)
        self.start()
        frame_bytes = self.process.stdout.read(
            self.video.player.info.pix_fmts.get(self.video.metadata.pix_fmt)
            * self.video.metadata.width
            * self.video.metadata.height
        )
        # print(
        #     f"[FFVideo {self.video.id}] decode video_frame: {self.frame}/{self.video.metadata.total_frames-1} - {self.video.starting_frame} {self.video.metadata.total_frames}"
        # )  # logger.info
        self.frame += 1
        if self.frame == self.video.metadata.total_frames:
            self.frame = 0
        self.process.stdout.flush()
        return frame_bytes
        # return None

    def set_frame(self, frame_number):
        # print(
        #     f"[FFVideo {self.video.id}] Setting frame {frame_number}"
        # )
        if 0 <= frame_number < self.video.metadata.total_frames:
            self.frame = frame_number
            self.stop()

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None


if __name__ == "__main__":
    environ["FFMPEG_BIN"] = "C:/Users/emaag/Downloads/ffmpeg/bin/ffmpeg.exe"
    environ["FFPROBE_BIN"] = "C:/Users/emaag/Downloads/ffmpeg/bin/ffprobe.exe"
    #     # FFMPEG_BIN = "D:/PROJECTS/GRISU/PIPELINE/extensions/bin/ffmpeg/bin/ffmpeg.exe"
    #     # FFPROBE_BIN = "D:/PROJECTS/GRISU/PIPELINE/extensions/bin/ffmpeg/bin/ffprobe.exe"
    VIDEO = r"C:\Users\emaag\Downloads\gri_108_030_140_01_comp_com_002.mp4"
    #     #     # VIDEO ="C:/Users/emaag/Downloads/test.mp4"
    player = FFMPEGPlayer()
    video = player.add_video(VIDEO)
    # pprint(video.metadata.data)
#     # video = player.add_video(VIDEO)
#     start = time.perf_counter()
#     player.initialize_decode()
#     print(player.end_frame / (time.perf_counter() - start))
