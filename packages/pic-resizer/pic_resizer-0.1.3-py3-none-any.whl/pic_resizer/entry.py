import io
from logging import debug, error
import logging
import os
import sys
import click
from PIL import Image
from .utils import filepath2basename_without_extension, parse_file_size


def image_resizing(origin: Image, target_size: int, file: str):
    (width, height) = (origin.size[0], origin.size[1])
    aspect_ratio = width / height
    l, r = 1, height
    for _ in range(10000):
        mid = (l + r) // 2
        resized = origin.resize([int(aspect_ratio * mid), mid])
        out = io.BytesIO()
        resized.save(out, format=origin.format)
        size = out.tell()
        debug(f"mid={mid}, size={size}")
        if size <= target_size:
            if target_size - size < target_size * 0.01:
                basename = filepath2basename_without_extension(file)
                resized.save(f"{basename}_resized.{origin.format.lower()}")
                break
            l = mid + 1
        else:
            r = mid
        out.flush()
    else:
        error("timeout")
        sys.exit(1)


@click.command()
@click.argument("file")
@click.option(
    "--size",
    "-s",
    required=True,
    type=str,
    default="100k",
    help="size of target image file, eg: 100k, 1M...",
)
def run(file: str, size):
    assert os.path.isfile(file), f"{file} is not a file"
    target_size = parse_file_size(size)
    assert os.stat(file).st_size > target_size, "image file is too small"
    with Image.open(file) as im:
        assert target_size, "target size is wrong"
        debug(f"target_size={target_size}")
        image_resizing(im, target_size, file)


def main():
    FORMAT = "%(asctime)s %(message)s"
    logging.basicConfig(format=FORMAT)
    sys.tracebacklimit = 0
    run()
