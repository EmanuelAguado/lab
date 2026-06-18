from os import environ, fspath
from pathlib import Path
from typing import List
from subprocess import run
from logging import getLogger

logger = getLogger(__name__)

class Nukema:  # Composition
    def __init__(
        self, output: Path, resolution: List[int] = [1920, 1080], fps: int = 24
    ):
        self._data_nodes = dict()
        self._data_composition = dict()
        self.fps = fps
        self.output = output
        self.id = 0
        self.id_filter = 0
        self.set_resolution(resolution)

    def add_audio(self, input_file: str):
        self._data_nodes["audio"] = {"cmd": f" -i {input_file}", "id": str(self.id)}
        self.id += 1

        return self._data_nodes["audio"]["id"]

    def add_crypto(
        self, input_file: str, type: str, node_name: str = "crypto", **kwargs
    ) -> str:
        """
        type: str = crypto_material, crypto_object
        """
        return self.add_input(
            input_file, node_name, preload=f'-layer "{type}"', **kwargs
        )

    def add_input(
        self,
        input_file: str,
        node_name: str = "input",
        preload: str = "",
        force_original_aspect_ratio: str = "decrease",
        format: str = None,
        opacity: float = None,
        color_space: str = "auto",
        scale: str = None,
        **kwargs,
    ) -> str:
        """
        force_original_aspect_ratio: str = decrease, increase.
        format: str = yuv420, yuv420p10, yuv422, yuv422p10, yuv444, rgb, gbrp, auto
        opacity: float = 0-1
        color_space: str = auto, bt709, fcc, bt601, smpte240m
        """
        if self._data_nodes.get(node_name):
            node_name += f"_{str(self.id)}"

        self._data_nodes[node_name] = {"cmd": "", "filter": "", "id": str(self.id)}
        if any(input_file.endswith(ext) for ext in [".exr"]):
            self._data_nodes[node_name][
                "cmd"
            ] = f" -framerate {self.fps} -apply_trc iec61966_2_1 {preload} -i {input_file}"
        elif any(input_file.endswith(ext) for ext in [".jpg"]):
            self._data_nodes[node_name][
                "cmd"
            ] = f" -framerate {self.fps} -i {input_file}"
        elif any(input_file.endswith(ext) for ext in [".mov", ".mp4"]):
            self._data_nodes[node_name]["cmd"] = f" -r {self.fps} -i {input_file}"

        # filter
        cmd_filter = list()
        if force_original_aspect_ratio:
            cmd_filter.append(
                f"scale={scale or self.resolution}:force_original_aspect_ratio={force_original_aspect_ratio}"
            )
        else:
            cmd_filter.append(f"scale={scale or self.resolution}")
        if color_space:
            cmd_filter.append(f"scale=out_color_matrix={color_space}")
        if format:
            cmd_filter.append(f"format={format}")
        if opacity:
            cmd_filter.append(f"colorchannelmixer=aa={opacity}")
        if kwargs:
            cmd_filter += [f"{k}={v}" for k, v in kwargs.items()]

        if cmd_filter:
            cmd_filter = ",".join(cmd_filter)
            self._data_nodes[node_name][
                "filter"
            ] = f'[{self._data_nodes[node_name]["id"]}:v]{cmd_filter}[{node_name}];'

        self.id += 1

        return node_name

    def merge(
        self,
        input_node_a: str,
        input_node_b: str,
        mode: str,
        opacity: float = 1,
        node_name: str = "merge",
    ):
        """

        mode: str = overlay, addition, multiply, vand, vaverage, vbleach,
            vburn, vdarken, vdifference, vdivide, vdodge, vexclusion,
            vextremity, vfreeze, vgeometric, vglow, vgrainextract, vgrainmerge,
            vhardlight, vhardmix, vhardoverlay, vharmonic, vheat, vinterpolate,
            vlighten, vlinearlight, vmultiply, vmultiply128, vnegation,
            vnormal, vor, voverlay, vphoenix, vpinlight, vreflect, vscreen,
            vsoftdifference, vsoftlight, vstain, vsubtract, vvividlight, vxor,
        opacity: float 0-1
        """
        if self._data_composition.get(node_name):
            node_name += f"_{str(self.id_filter)}"
            self.id_filter += 1

        if mode == "overlay":
            cmd = mode
        elif mode.startswith("overlay"):
            cmd = mode
        else:
            cmd = f"blend=all_mode={mode}:all_opacity={opacity}"

        self._data_composition[node_name] = (
            f"[{input_node_a}][{input_node_b}]{cmd},format=gbrp[{node_name}];"
        )

        return node_name

    def merge_alpha(
        self, input_node: str, input_node_alpha: str, node_name: str = "mergealpha"
    ):
        if self._data_composition.get(node_name):
            node_name += f"_{str(self.id_filter)}"
            self.id_filter += 1

        self._data_composition[node_name] = (
            f"[{input_node}][{input_node_alpha}]alphamerge[{node_name}];"
        )

        return node_name

    def generate_cmd(self):

        cmd = f'{environ.get("FFMPEG_BIN")} -y'

        for node_name in self._data_nodes.keys():
            cmd += self._data_nodes[node_name]["cmd"]

        cmd += ' -vcodec libx264 -profile:v high444 -filter_complex "'

        for name in self._data_nodes.keys():
            if name == "audio":
                continue
            cmd += self._data_nodes[name]["filter"]

        last_filter = None
        for name in self._data_composition.keys():
            cmd += self._data_composition[name]
            last_filter = name
        if last_filter:
            cmd += f"[{last_filter}]format=yuva420p[out]"

        map_audio = ""
        if self._data_nodes.get("audio"):
            map_audio = f'-map {self._data_nodes["audio"]["id"]}:a'

        if len(list(self._data_nodes.keys())) > 1:
            out = "out"
        else:
            out = node_name
        cmd += (
            f'" -preset ultrafast -crf 1 -map [{out}] {map_audio} {fspath(self.output)}'
        )

        return cmd.strip()

    def render(self):
        cmd = self.generate_cmd()
        print(cmd)
        run(cmd)
        return self.output

    def set_resolution(self, resolution: List[int]):
        self.resolution = f"{resolution[0]}:{resolution[1]}"