# type: ignore
from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from time import perf_counter
from typing import Callable, NoReturn

import av

from auto_editor.vanparse import ArgumentParser

av.logging.set_level(av.logging.PANIC)


@dataclass
class TestArgs:
    only: list[str] = field(default_factory=list)
    help: bool = False
    category: str = "cli"


def test_options(parser):
    parser.add_argument("--only", "-n", nargs="*")
    parser.add_required(
        "category",
        nargs=1,
        choices=["cli", "sub", "api", "unit", "all"],
        help="Set what category of tests to run.",
    )
    return parser


def pipe_to_console(cmd: list[str]) -> tuple[int, str, str]:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode("utf-8"), stderr.decode("utf-8")


def cleanup(the_dir: str) -> None:
    for item in os.listdir(the_dir):
        item = os.path.join(the_dir, item)
        if (
            "_ALTERED" in item
            or item.endswith(".xml")
            or item.endswith(".fcpxml")
            or item.endswith(".mlt")
        ):
            os.remove(item)
        if item.endswith("_tracks"):
            shutil.rmtree(item)


def clean_all() -> None:
    cleanup("resources")
    cleanup(os.getcwd())


def get_runner() -> list[str]:
    if platform.system() == "Windows":
        return ["py", "-m", "auto_editor"]
    return ["python3", "-m", "auto_editor"]


def run_program(cmd: list[str]) -> None:
    no_open = "." in cmd[0]
    cmd = get_runner() + cmd

    if no_open:
        cmd += ["--no_open"]

    returncode, stdout, stderr = pipe_to_console(cmd)
    if returncode > 0:
        raise Exception(f"{stdout}\n{stderr}\n")


def check_for_error(cmd: list[str], match=None) -> None:
    returncode, stdout, stderr = pipe_to_console(get_runner() + cmd)
    if returncode > 0:
        if "Error!" in stderr:
            if match is not None and match not in stderr:
                raise Exception(f'Could\'t find "{match}"')
        else:
            raise Exception(f"Program crashed.\n{stdout}\n{stderr}")
    else:
        raise Exception("Program should not respond with a code 0.")


class Tester:
    def __init__(self, args: TestArgs) -> None:
        self.passed_tests = 0
        self.failed_tests = 0
        self.args = args

    def run(self, func: Callable, cleanup=None, allow_fail=False) -> None:
        if self.args.only != [] and func.__name__ not in self.args.only:
            return

        start = perf_counter()
        try:
            func()
            end = perf_counter() - start
        except KeyboardInterrupt:
            print(f"Testing Interrupted by User.")
            clean_all()
            sys.exit(1)
        except Exception as e:
            self.failed_tests += 1
            print(f"Test '{func.__name__}' failed.\n{e}")
            if not allow_fail:
                logging.error("", exc_info=True)
                clean_all()
                sys.exit(1)
        else:
            self.passed_tests += 1
            print(f"Test '{func.__name__}' passed: {round(end, 2)} secs")
            if cleanup is not None:
                cleanup()

    def end(self) -> NoReturn:
        print(f"{self.passed_tests}/{self.passed_tests + self.failed_tests}")
        clean_all()
        sys.exit(0)


def main(sys_args: list[str] | None = None):
    if sys_args is None:
        sys_args = sys.argv[1:]

    args = test_options(ArgumentParser("test")).parse_args(TestArgs, sys_args)

    ### Tests ###

    ## API Tests ##

    def read_api_0_1():
        check_for_error(
            ["resources/json/0.1-non-zero-start.json"],
            "Error! First chunk must start with 0",
        )
        check_for_error(
            ["resources/json/0.1-disjoint.json"], "Error! Chunk disjointed at"
        )

    def help_tests():
        """check the help option, its short, and help on options and groups."""
        run_program(["--help"])
        run_program(["-h"])
        run_program(["--frame_margin", "--help"])
        run_program(["--frame_margin", "-h"])
        run_program(["--help", "--help"])
        run_program(["-h", "--help"])
        run_program(["--help", "-h"])
        run_program(["-h", "--help"])

    def version_test():
        """Test version flags and debug by itself."""
        run_program(["--version"])
        run_program(["-v"])
        run_program(["-V"])
        run_program(["--debug"])

    def parser_test():
        check_for_error(["example.mp4", "--video-speed"], "needs argument")

    def info():
        run_program(["info", "example.mp4"])
        run_program(["info", "resources/only-video/man-on-green-screen.mp4"])
        run_program(["info", "resources/multi-track.mov"])
        run_program(["info", "resources/new-commentary.mp3"])
        run_program(["info", "resources/testsrc.mkv"])

    def levels():
        run_program(["levels", "resources/multi-track.mov"])
        run_program(["levels", "resources/new-commentary.mp3"])

    def subdump():
        run_program(["subdump", "resources/subtitle.mp4"])

    def grep():
        run_program(["grep", "boop", "resources/subtitle.mp4"])

    def desc():
        run_program(["desc", "example.mp4"])

    def example_tests():
        run_program(["example.mp4", "--video_codec", "uncompressed"])
        with av.open("example_ALTERED.mp4") as cn:
            video = cn.streams.video[0]
            assert video.average_rate == 30
            assert video.time_base == Fraction(1, 30)
            assert video.width == 1280
            assert video.height == 720
            assert video.codec.name == "mpeg4"
            assert cn.streams.audio[0].codec.name == "aac"
            assert cn.streams.audio[0].rate == 48000

        run_program(["example.mp4"])
        with av.open("example_ALTERED.mp4") as cn:
            video = cn.streams.video[0]
            assert video.average_rate == 30
            assert video.time_base == Fraction(1, 30)
            assert video.width == 1280
            assert video.height == 720
            assert video.codec.name == "h264"
            assert cn.streams.audio[0].codec.name == "aac"
            assert cn.streams.audio[0].rate == 48000
            assert video.language == "eng"
            assert cn.streams.audio[0].language == "eng"

    # PR #260
    def high_speed_test():
        run_program(["example.mp4", "--video-speed", "99998"])

    # Issue #288
    def expand_chunks():
        run_program(
            ["example.mp4", "--silent-speed", "1", "-o", "out.json"]
        )
        with open("out.json") as file:
            api = json.load(file)
        assert len(api["chunks"]) > 4, "Chunks should not combine"
        os.remove("out.json")

    # Issue #184
    def unit_tests():
        run_program(
            ["example.mp4", "--mark_as_loud", "20s,22sec", "25secs,26.5seconds"]
        )
        run_program(["example.mp4", "--edit", "all", "--set-speed", "125%,-30,end"])
        run_program(["example.mp4", "--sample_rate", "44_100"])
        run_program(["example.mp4", "--margin", "3_0"])
        run_program(["example.mp4", "--sample_rate", "44100 Hz"])
        run_program(["example.mp4", "--sample_rate", "44.1 kHz"])
        run_program(["example.mp4", "--edit", "audio:threshold=4%"])


    def video_speed():
        run_program(["example.mp4", "--video-speed", "1.5"])

    def backwards_range_test():
        """
        Cut out the last 5 seconds of a media file by using negative number in the
        range.
        """
        run_program(["example.mp4", "--edit", "none", "--cut_out", "-5secs,end"])
        run_program(["example.mp4", "--edit", "all", "--add_in", "-5secs,end"])

    def cut_out_test():
        run_program(
            [
                "example.mp4",
                "--edit",
                "none",
                "--video_speed",
                "2",
                "--silent_speed",
                "3",
                "--cut_out",
                "2secs,10secs",
            ]
        )
        run_program(
            [
                "example.mp4",
                "--edit",
                "all",
                "--video_speed",
                "2",
                "--add_in",
                "2secs,10secs",
            ]
        )

    def gif_test():
        """
        Feed auto-editor a gif file and make sure it can spit out a correctly formated
        gif. No editing is requested.
        """
        run_program(["resources/only-video/man-on-green-screen.gif", "--edit", "none"])
        with av.open("resources/only-video/man-on-green-screen_ALTERED.gif") as cn:
            assert cn.streams.video[0].codec.name == "gif"

    def margin_tests():
        run_program(["example.mp4", "-m", "3"])
        run_program(["example.mp4", "--margin", "3"])
        run_program(["example.mp4", "-m", "0.3sec"])
        run_program(["example.mp4", "-m", "6f,-3secs"])
        run_program(["example.mp4", "-m", "3,5 frames"])
        run_program(["example.mp4", "-m", "0.4 seconds"])

    def input_extension():
        """Input file must have an extension. Throw error if none is given."""

        shutil.copy("example.mp4", "example")
        check_for_error(["example", "--no_open"], "must have an extension.")
        os.remove("example")

    def output_extension():
        # Add input extension to output name if no output extension is given.
        run_program(["example.mp4", "-o", "out"])
        with av.open("out.mp4") as cn:
            assert cn.streams.video[0].codec.name == "h264"

        os.remove("out.mp4")

        run_program(["resources/testsrc.mkv", "-o", "out"])
        with av.open("out.mkv") as cn:
            assert cn.streams.video[0].codec.name == "h264"

        os.remove("out.mkv")

    def progress_ops_test():
        run_program(["example.mp4", "--progress", "machine"])
        run_program(["example.mp4", "--progress", "none"])
        run_program(["example.mp4", "--progress", "ascii"])

    def silent_threshold():
        run_program(["resources/new-commentary.mp3", "--edit", "audio:threshold=0.1"])

    def track_tests():
        run_program(["resources/multi-track.mov", "--keep_tracks_seperate"])

    def json_tests():
        run_program(["example.mp4", "--export_as_json"])
        run_program(["example.json"])

    def resolution_and_scale():
        run_program(["example.mp4", "--scale", "1.5"])
        with av.open("example_ALTERED.mp4") as cn:
            assert cn.streams.video[0].average_rate == 30
            assert cn.streams.video[0].width == 1920
            assert cn.streams.video[0].height == 1080
            assert cn.streams.audio[0].rate == 48000

        run_program(["example.mp4", "--scale", "0.2"])
        with av.open("example_ALTERED.mp4") as cn:
            assert cn.streams.video[0].average_rate == 30
            assert cn.streams.video[0].width == 256
            assert cn.streams.video[0].height == 144
            assert cn.streams.audio[0].rate == 48000

        run_program(["example.mp4", "-res", "700,380", "-b", "darkgreen"])
        with av.open("example_ALTERED.mp4") as cn:
            assert cn.streams.video[0].average_rate == 30
            assert cn.streams.video[0].width == 700
            assert cn.streams.video[0].height == 380
            assert cn.streams.audio[0].rate == 48000

    def obj_makes_video():
        run_program(
            [
                "resources/new-commentary.mp3",
                "--add-rectangle",
                "0,30,0,0,300,300,fill=blue",
                "-o",
                "out.mp4",
            ]
        )
        with av.open("out.mp4") as cn:
            assert len(cn.streams.video) == 1
            assert len(cn.streams.audio) == 1
            assert cn.streams.video[0].width == 1920
            assert cn.streams.video[0].height == 1080
            assert cn.streams.video[0].average_rate == 30

    def various_errors_test():
        check_for_error(
            ["example.mp4", "--add_rectangle", "0,60", "--cut_out", "60,end"]
        )

    def render_video_objs():
        run_program(
            [
                "resources/testsrc.mp4",
                "--mark_as_loud",
                "start,end",
                "--add_rectangle",
                "0,30,0,200,100,300,fill=#43FA56,stroke=10",
            ]
        )
        os.remove("resources/testsrc_ALTERED.mp4")

        # Every element should be visible, order should be preserved.
        run_program(
            [
                "example.mp4",
                "--add-ellipse",
                "0,30,50%,50%,300,300,fill=red",
                "--add-rectangle",
                "0,30,500,440,400,200,fill=skyblue",
                "--add-ellipse",
                "0,30,50%,50%,100,100,fill=darkgreen",
                "--edit",
                "none",
                "--cut-out",
                "30,end",
            ]
        )

        # Both ellipses should be visible
        run_program(
            [
                "example.mp4",
                "--add-ellipse",
                "0,60,50%,50%,300,300,fill=darkgreen",
                "0,30,50%,50%,200,200,fill=green",
                "--edit",
                "none",
                "--cut-out",
                "60,end",
            ]
        )

    def render_text():
        run_program(["example.mp4", "--add-text", "0,30,This is my text,font=default"])

    def check_font_error():
        check_for_error(
            ["example.mp4", "--add-text", "0,30,text,0,0,notafont"], "not found"
        )

    def export_tests():
        for test_name in (
            "aac.m4a",
            "alac.m4a",
            "wav/pcm-f32le.wav",
            "wav/pcm-s32le.wav",
            "multi-track.mov",
            "subtitle.mp4",
            "testsrc.mkv",
        ):

            test_file = f"resources/{test_name}"
            run_program([test_file])
            run_program([test_file, "--edit", "none"])
            run_program([test_file, "-exp"])
            run_program([test_file, "-exf"])
            run_program([test_file, "-exs"])
            run_program([test_file, "--export_as_clip_sequence"])
            run_program([test_file, "--preview"])
            cleanup("resources")

    def codec_tests():
        run_program(["example.mp4", "--video_codec", "h264"])
        run_program(["example.mp4", "--audio_codec", "ac3"])

    def combine():
        run_program(["example.mp4", "--mark_as_silent", "0,171", "-o", "hmm.mp4"])
        run_program(["example.mp4", "hmm.mp4", "--combine-files", "--debug"])
        os.remove("hmm.mp4")

    # Issue #241
    def multi_track_edit():
        run_program(
            [
                "example.mp4",
                "resources/multi-track.mov",
                "--edit",
                "audio:stream=1",
                "-o",
                "out.mov",
            ]
        )
        with av.open("out.mov", "r") as cn:
            assert len(cn.streams.audio) == 1

    def concat_mux_tracks():
        run_program(["example.mp4", "resources/multi-track.mov", "-o", "out.mov"])
        with av.open("out.mov", "r") as cn:
            assert len(cn.streams.audio) == 1

    def concat_multiple_tracks():
        run_program(
            [
                "resources/multi-track.mov",
                "resources/multi-track.mov",
                "--keep-tracks-separate",
                "-o",
                "out.mov",
            ]
        )
        with av.open("out.mov", "r") as cn:
            assert len(cn.streams.audio) == 2, f"audio streams: {len(cn.streams.audio)}"

        run_program(
            [
                "example.mp4",
                "resources/multi-track.mov",
                "--keep-tracks-separate",
                "-o",
                "out.mov",
            ]
        )
        with av.open("out.mov", "r") as cn:
            assert len(cn.streams.audio) == 2
        os.remove("out.mov")

    def frame_rate():
        run_program(["example.mp4", "-r", "15", "--no-seek"])
        with av.open("example_ALTERED.mp4", "r") as cn:
            video = cn.streams.video[0]
            assert video.average_rate == 15
            assert video.time_base == Fraction(1, 15)
            dur = float(video.duration * video.time_base)
            assert dur - 17.33333333333333333333333 < 3

        run_program(["example.mp4", "-r", "20"])
        with av.open("example_ALTERED.mp4", "r") as cn:
            video = cn.streams.video[0]
            assert video.average_rate == 20
            assert video.time_base == Fraction(1, 20)
            dur = float(video.duration * video.time_base)
            assert dur - 17.33333333333333333333333 < 2

        run_program(["example.mp4", "-r", "60"])
        with av.open("example_ALTERED.mp4", "r") as cn:
            video = cn.streams.video[0]
            assert video.average_rate == 60
            assert video.time_base == Fraction(1, 60)
            dur = float(video.duration * video.time_base)
            assert dur - 17.33333333333333333333333 < 0.3

    def image_test():
        run_program(["resources/embedded-image/h264-png.mp4"])
        with av.open("resources/embedded-image/h264-png_ALTERED.mp4", "r") as cn:
            assert cn.streams.video[0].codec.name == "h264"
            assert cn.streams.video[1].codec.name == "png"

        run_program(["resources/embedded-image/h264-mjpeg.mp4"])
        with av.open("resources/embedded-image/h264-mjpeg_ALTERED.mp4", "r") as cn:
            assert cn.streams.video[0].codec.name == "h264"
            assert cn.streams.video[1].codec.name == "mjpeg"

        run_program(["resources/embedded-image/h264-png.mkv"])
        with av.open("resources/embedded-image/h264-png_ALTERED.mkv", "r") as cn:
            assert cn.streams.video[0].codec.name == "h264"
            assert cn.streams.video[1].codec.name == "png"

        run_program(["resources/embedded-image/h264-mjpeg.mkv"])
        with av.open("resources/embedded-image/h264-mjpeg_ALTERED.mkv", "r") as cn:
            assert cn.streams.video[0].codec.name == "h264"
            assert cn.streams.video[1].codec.name == "mjpeg"

    def motion_tests():
        run_program(
            [
                "resources/only-video/man-on-green-screen.mp4",
                "--edit",
                "motion",
                "--debug",
                "--frame_margin",
                "0",
                "-mcut",
                "0",
                "-mclip",
                "0",
            ]
        )
        run_program(
            [
                "resources/only-video/man-on-green-screen.mp4",
                "--edit",
                "motion:threshold=0",
            ]
        )

    def edit_positive_tests():
        run_program(["resources/multi-track.mov", "--edit", "audio:stream=all"])
        run_program(["resources/multi-track.mov", "--edit", "not audio:stream=all"])
        run_program(
            [
                "resources/multi-track.mov",
                "--edit",
                "not audio:threshold=4% or audio:stream=1",
            ]
        )
        # run_program(['resources/multi-track.mov', '--edit', 'not audio:threshold=4% or not audio:stream=1'])

    def edit_negative_tests():
        check_for_error(
            ["resources/wav/example-cut-s16le.wav", "--edit", "motion"],
            "Video stream '0' does not exist",
        )
        check_for_error(
            ["resources/only-video/man-on-green-screen.gif", "--edit", "audio"],
            "Audio stream '0' does not exist",
        )
        check_for_error(
            ["example.mp4", "--edit", "not"], "Error! Dangling operand: 'not'"
        )
        check_for_error(
            ["example.mp4", "--edit", "audio and"], "Error! Dangling operand: 'and'"
        )
        check_for_error(
            ["example.mp4", "--edit", "and"],
            "Error! 'and' operand needs two arguments.",
        )
        check_for_error(
            ["example.mp4", "--edit", "and audio"],
            "Error! 'and' operand needs two arguments.",
        )
        check_for_error(
            ["example.mp4", "--edit", "or audio"],
            "Error! 'or' operand needs two arguments.",
        )
        check_for_error(
            ["example.mp4", "--edit", "audio four audio"],
            "Error! Unknown method/operator: 'four'",
        )
        check_for_error(
            ["example.mp4", "--edit", "audio audio"],
            "Logic operator must be between two editing methods",
        )

    def yuv442p():
        run_program(["resources/test_yuv422p.mp4"])

    #  Issue 280
    def SAR():
        run_program(["resources/SAR-2by3.mp4"])
        with av.open("resources/SAR-2by3_ALTERED.mp4") as cn:
            assert cn.streams.video[0].sample_aspect_ratio == Fraction(2, 3)

    tests = []

    if args.category in ("api", "all"):
        tests.append(read_api_0_1)

    if args.category in ("sub", "all"):
        tests.extend([info, levels, subdump, grep, desc])

    if args.category in ("cli", "all"):
        tests.extend(
            [
                video_speed,
                expand_chunks,
                SAR,
                yuv442p,
                obj_makes_video,
                edit_positive_tests,
                edit_negative_tests,
                multi_track_edit,
                concat_mux_tracks,
                concat_multiple_tracks,
                render_video_objs,
                resolution_and_scale,
                various_errors_test,
                render_text,
                check_font_error,
                frame_rate,
                help_tests,
                version_test,
                parser_test,
                combine,
                example_tests,
                export_tests,
                high_speed_test,
                unit_tests,
                backwards_range_test,
                cut_out_test,
                image_test,
                gif_test,
                margin_tests,
                input_extension,
                output_extension,
                progress_ops_test,
                silent_threshold,
                track_tests,
                json_tests,
                codec_tests,
                motion_tests,
            ]
        )

    tester = Tester(args)

    for test in tests:
        tester.run(test)

    tester.end()


if __name__ == "__main__":
    main()
