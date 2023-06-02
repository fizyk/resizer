"""Main resizer module."""
import pathlib
from collections import defaultdict
from queue import SimpleQueue
from typing import Any, Dict, Generator

import click
from click import Context
from PIL import Image


@click.group()
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path))
@click.pass_context
def resizer(ctx: Context, path: pathlib.Path) -> None:
    """Resizer command group."""
    ctx.ensure_object(dict)
    ctx.obj["path"] = path


@resizer.command()
@click.pass_context
def stats(ctx: Context) -> None:
    """Print path's images stats."""
    ctx.ensure_object(dict)
    path = ctx.obj["path"]
    click.echo(f"Reading images to process from {path.absolute()}")
    count = image_stats(list_images(path))
    click.echo(f"There's a total of {count} images.")
    pass


@resizer.command()
@click.option("--max-size", type=int)
@click.pass_context
def resize(ctx: Context, max_size: int) -> None:
    """Resize images in given path."""
    ctx.ensure_object(dict)
    path = ctx.obj["path"]
    click.echo(f"Reading images to process from {path.absolute()}")
    images_count = count_images(path)
    click.echo(f"Found {images_count} image files.")
    resize_images(list_images(path), max_size, images_count)


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


def resize_images(images: Generator[pathlib.Path, None, None], max_size, images_count: int) -> None:
    """Resize images."""
    with click.progressbar(images, show_percent=True, show_pos=True, length=images_count) as bar:
        for image_file in bar:
            resize_image(image_file, image_file, max_size)


def resize_image(image_file, destination: pathlib.Path, max_size) -> None:
    """Resize given image to defined destination."""
    with Image.open(image_file) as image:
        width = image.width
        height = image.height
        if width <= max_size and height <= max_size:
            return
        if image.width > image.height:
            height = height * (max_size / width)
            width = max_size
        else:
            width = width * (max_size / height)
            height = max_size
        new_image = image.resize((int(width), int(height)), Image.Resampling.LANCZOS)
        kwargs: Dict[str, Any] = {"quality": 75}
        if exif := image.info.get("exif"):
            kwargs["exif"] = exif
    try:
        new_image.save(destination, **kwargs)
    except ValueError as e:
        click.echo(f"Encountered {e} while processing the {image_file}")
    new_image.close()
