"""Statistic gathering methods."""
import pathlib
from collections import defaultdict
from queue import SimpleQueue
from typing import Dict, Generator

import click
from PIL import Image


def list_images(path: pathlib.Path) -> Generator[pathlib.Path, None, None]:
    """List all images from path."""
    directories: SimpleQueue[pathlib.Path] = SimpleQueue()
    directories.put(path)
    while not directories.empty():
        current_directory = directories.get()
        for children_path in current_directory.iterdir():
            if children_path.is_dir():
                directories.put(children_path)
            else:
                try:
                    with Image.open(children_path):
                        yield children_path
                except IOError:
                    pass


def count_images(path):
    """Count all images in a path."""
    return sum(1 for _ in list_images(path))


def image_stats(images: Generator[pathlib.Path, None, None]) -> int:
    """Actual print all images statistics."""
    size_stat: Dict = defaultdict(int)
    images_count = 0
    for image_file in images:
        with Image.open(image_file) as image:
            if image.width > image.height:
                size = (image.width, image.height)
            else:
                size = (image.height, image.width)
            size_stat[size] += 1
            images_count += 1
    click.echo("Sizes:")
    for size, count in size_stat.items():
        click.echo(f" {size[0]:5}x{size[1]:<5}: {count:6}")

    return images_count
