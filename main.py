import pathlib
from collections import defaultdict
from queue import SimpleQueue
from typing import Dict, Generator, Tuple, Optional, Union

import PIL.TiffImagePlugin
import click
from PIL import Image
from click import Context


@click.group()
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path))
@click.pass_context
def resizer(ctx: Context, path: pathlib.Path) -> None:
    ctx.ensure_object(dict)
    ctx.obj["path"] = path


@resizer.command()
@click.pass_context
def stats(ctx: Context) -> None:
    ctx.ensure_object(dict)
    path = ctx.obj["path"]
    click.echo(f"Reading images to process from {path.absolute()}")
    count = image_stats(list_images(path))
    click.echo(f"There's a total of {count} images.")
    pass


@resizer.command()
@click.option("--max-size", type=int)
@click.option("--dpi", type=int)
@click.pass_context
def resize(ctx: Context, max_size: int, dpi: int) -> None:
    ctx.ensure_object(dict)
    path = ctx.obj["path"]
    click.echo(f"Reading images to process from {path.absolute()}")
    images_count = count_images(path)
    click.echo(f"Found {images_count} image files.")
    resize_images(list_images(path), max_size, dpi, images_count)


def list_images(path: pathlib.Path) -> Generator[pathlib.Path, None, None]:
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
    return sum(1 for _ in list_images(path))


def extract_dpis(image :Image) -> Optional[Tuple[Union[int, float], Union[int, float]]]:
    dpis = image.info.get("dpi")
    if not dpis:
        return
    if isinstance(dpis[0], PIL.TiffImagePlugin.IFDRational):
        return float(dpis[0]), float(dpis[1])
    return dpis


def image_stats(images: Generator[pathlib.Path, None, None]) -> int:
    size_stat: Dict = defaultdict(int)
    dpi_stat: Dict = defaultdict(int)
    images_count = 0
    for image_file in images:
        with Image.open(image_file) as image:
            if image.width > image.height:
                size = (image.width, image.height)
            else:
                size = (image.height, image.width)
            dpi_stat[extract_dpis(image)] += 1
            size_stat[size] += 1
            images_count += 1
    click.echo("Sizes:")
    for size, count in size_stat.items():
        click.echo(f" {size[0]:5}x{size[1]:<5}: {count:6}")
    click.echo("DPIs:")
    for dpi, count in dpi_stat.items():
        if dpi:
            click.echo(f" {dpi[0]:3}x{dpi[1]:<3}: {count:4}")
        else:
            click.echo(f"      - : {count:4}")

    return images_count


def resize_images(images: Generator[pathlib.Path, None, None], max_size, defined_dpi, images_count: int) -> None:
    with click.progressbar(images, show_percent=True, show_pos=True, length=images_count) as bar:
        for image_file in bar:
            with Image.open(image_file) as image:
                width = image.width
                height = image.height
                if width <= max_size and height <= max_size:
                    continue
                if image.width > image.height:
                    height = height * (max_size / width)
                    width = max_size
                else:
                    width = width * (max_size / height)
                    height = max_size
                new_image = image.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                kwargs = {"quality": 75}
                if dpi := extract_dpis(image):
                    if dpi[0] > defined_dpi:
                        kwargs["dpi"] = (defined_dpi, defined_dpi)
                if exif := image.info.get("exif"):
                    kwargs["exif"] = exif
            try:
                new_image.save(image_file, **kwargs)
            except ValueError as e:
                click.echo(f"Encountered {e} while processing the {image_file}")
            new_image.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    resizer()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
