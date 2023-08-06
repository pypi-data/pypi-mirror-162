from logging import debug
import logging
import os
import sys
import click
from PIL import Image
from .utils import parse_file_size
from .lib import image_resizing
from .web import serve
from .utils import filepath2basename_without_extension
from . import __version__


@click.command(help="Operating from the command line")
@click.argument("file")
@click.option(
    "--size",
    "-s",
    type=str,
    default="100k",
    help="Size of target image file, eg: 100k, 1M...",
)
def cli(file: str, size):
    assert os.path.isfile(file), f"{file} is not a file"
    target_size = parse_file_size(size)
    assert os.stat(file).st_size > target_size, "Image file is too small"
    with Image.open(file) as im:
        assert target_size, "Target size is wrong"
        assert target_size >= 2000, "Target size is too small"
        debug(f"target_size={target_size}")
        basename = filepath2basename_without_extension(file)
        image_resizing(im, target_size).save(
            f"{basename}_resized.{im.format.lower()}",
            format=im.format,
            quality=75,
            subsampling=0,
        )


@click.command(help="Operating in the web app")
def web():
    click.echo("in web")
    serve()


@click.version_option(__version__)
@click.group()
def run():
    pass


run.add_command(cli)
run.add_command(web)


def main():
    FORMAT = "%(asctime)s %(message)s"
    logging.basicConfig(format=FORMAT)
    sys.tracebacklimit = 0
    run()
