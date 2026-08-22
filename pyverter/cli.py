"""Main pyverter module."""

import pathlib

import click
from click import Context

from pyverter.resize import Resizer
from pyverter.stat import image_stats, list_images


@click.group()
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path))
@click.pass_context
def pyverter(ctx: Context, path: pathlib.Path) -> None:
    """Pyverter command group."""
    ctx.ensure_object(dict)
    ctx.obj["path"] = path


@pyverter.command()
@click.pass_context
def stats(ctx: Context) -> None:
    """Print path's images stats."""
    ctx.ensure_object(dict)
    path = ctx.obj["path"]
    click.echo(f"Reading images to process from {path.absolute()}")
    count = image_stats(list_images(path))
    click.echo(f"There's a total of {count} images.")
    pass


@pyverter.command()
@click.option("--max-size", type=int)
@click.pass_context
def resize(ctx: Context, max_size: int) -> None:
    """Resize images in given path."""
    ctx.ensure_object(dict)
    path = ctx.obj["path"]
    resizer = Resizer(max_size, path, path)
    resizer()
