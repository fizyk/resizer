"""Resize algorithm."""

import multiprocessing
import pathlib
import signal
from multiprocessing import Process, Queue
from multiprocessing.synchronize import Event
from queue import Empty
from typing import Any, Dict, List, NamedTuple

import click
from PIL import Image

from resizer.stat import list_images


class ProcessedImages(NamedTuple):
    """Processed image message."""

    image_path: pathlib.Path
    width: int
    height: int
    processed: bool
    error: Exception | None


class NonInteruptableProcess(Process):
    """Catch signal interrupt for processes."""

    def run(self) -> None:
        """Run process but immune to SIGINT."""
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        super().run()


class Resizer:
    """Resizer algorithm."""

    def __init__(self, max_size: int, source: pathlib.Path, destination: pathlib.Path) -> None:
        """Initialize resizer."""
        self.cpu_cores: int = multiprocessing.cpu_count()
        self.max_size = max_size
        self.source = source
        self.destination = destination

    def __call__(self) -> None:
        """Run resizer."""
        stop_event: Event = multiprocessing.Event()
        process_no: int = int(self.cpu_cores / 2)

        # initial shard queue
        images_to_process: Queue = Queue()
        images_processed: Queue = Queue()

        processes: List[NonInteruptableProcess] = []
        for _ in range(process_no):
            process = NonInteruptableProcess(
                target=self.process_images,
                args=(images_to_process, images_processed, stop_event),
            )
            processes.append(process)
            process.start()

        click.echo(f"Reading images to process from {self.source.absolute()}")
        image_counter: int = 0
        for image in list_images(self.source):
            images_to_process.put(image)
            image_counter += 1
        click.echo(f"Found {image_counter} image files.")

        converted: List[ProcessedImages] = []
        skipped: List[ProcessedImages] = []
        errored: List[ProcessedImages] = []
        try:
            with click.progressbar(
                show_percent=True, show_pos=True, length=image_counter, label="Processing images"
            ) as bar:
                processed_counter: int = 0
                while True:
                    try:
                        image_processed: ProcessedImages = images_processed.get(timeout=5)
                    except Empty:
                        break
                    processed_counter += 1
                    bar.update(1)
                    if image_processed.processed:
                        converted.append(image_processed)
                    else:
                        skipped.append(image_processed)
                        if image_processed.error:
                            errored.append(image_processed)
                    if processed_counter >= image_counter:
                        break
        except KeyboardInterrupt:
            click.echo("Process stopped")
        finally:
            click.echo("Finished")
            stop_event.set()
            for process in processes:
                process.join()
        click.echo(f" {len(converted)} of images got converted and {len(skipped)} got skipped.")
        if errored:
            click.echo(f" There were {len(errored)} errors.")
            for errored_image in errored:
                click.echo(f" {errored_image.image_path} errored with f{errored_image.error}")

    def process_images(self, to_process: Queue, processed: Queue, stop: Event) -> None:
        """Process images, one at a time."""
        while True:
            if stop.is_set():
                break
            try:
                image_file: pathlib.Path = to_process.get(timeout=3)
            except Empty:
                continue
            image_file.relative_to(self.source)
            destination = self.destination / image_file.relative_to(self.source)
            try:
                processed.put(self.resize_image(image_file, destination))
            except OSError as ex:
                processed.put(ProcessedImages(image_file, 0, 0, True, ex))

    def resize_image(self, image_file: pathlib.Path, destination: pathlib.Path) -> ProcessedImages:
        """Resize image, return true if the resize had been performed."""
        with Image.open(image_file) as image:
            if image.width <= self.max_size and image.height <= self.max_size:
                return ProcessedImages(destination, image.width, image.height, False, None)
            if image.width > image.height:
                height = int(image.height * self.max_size / image.width)
                width = self.max_size
            else:
                width = int(image.width * self.max_size / image.height)
                height = self.max_size
            new_image = image.resize((int(width), int(height)), Image.Resampling.LANCZOS)
            kwargs: Dict[str, Any] = {"quality": 75}
            if exif := image.info.get("exif"):
                kwargs["exif"] = exif
            try:
                new_image.save(destination, **kwargs)
                return ProcessedImages(destination, width, height, True, None)
            except ValueError:
                return ProcessedImages(destination, width, height, False, None)
            finally:
                new_image.close()
