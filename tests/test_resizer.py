"""Resizer tests."""
from pathlib import Path
from typing import Generator

import pytest
from PIL import Image
from pytest import FixtureRequest

from resizer.resize import Resizer
from resizer.stat import count_images, list_images

SAMPLE_IMAGE_NAME = "DALL·E generated art.png"


@pytest.fixture
def samples_path(request: FixtureRequest) -> Path:
    """Return test root path."""
    return request.path.parent.joinpath("samples")


@pytest.fixture
def destination_image(tmp_path: Path) -> Generator[Path, None, None]:
    """Return path for destination image and clean after wards."""
    destination_image = tmp_path / SAMPLE_IMAGE_NAME
    yield destination_image
    destination_image.unlink(True)


def test_list_images(samples_path: Path) -> None:
    """Check proper image listing."""
    image_paths = list(list_images(samples_path))
    assert len(image_paths) == 1
    assert image_paths[0].name == "DALL·E generated art.png"


def test_count_images(samples_path: Path) -> None:
    """Check proper image counting."""
    assert count_images(samples_path) == 1


def test_resize_image(samples_path, destination_image, tmp_path: Path) -> None:
    """Check that image gets resized."""
    source_image = samples_path / SAMPLE_IMAGE_NAME
    resizer = Resizer(source=samples_path, destination=tmp_path, max_size=300)
    resizer.resize_image(source_image, destination_image)
    with Image.open(destination_image) as test_result:
        assert test_result.width == 300
        assert test_result.height == 160
