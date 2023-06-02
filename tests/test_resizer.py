"""Resizer tests."""
from pathlib import Path
from typing import Generator

import pytest
from PIL import Image
from pytest import FixtureRequest

from resizer.main import count_images, list_images, resize_image

SAMPLE_IMAGE_NAME = "DALL·E generated art.png"

SAMPLE_IMAGE_NAME_PATH = "samples/DALL·E generated art.png"


@pytest.fixture
def root_path(request: FixtureRequest) -> Path:
    """Return test root path."""
    return request.path.parent


@pytest.fixture
def destination_image(tmp_path: Path) -> Generator[Path, None, None]:
    """Return path for destination image and clean after wards."""
    destination_image = tmp_path / SAMPLE_IMAGE_NAME
    yield destination_image
    destination_image.unlink(True)


def test_list_images(root_path: Path) -> None:
    """Check proper image listing."""
    image_paths = list(list_images(root_path.joinpath("samples")))
    assert len(image_paths) == 1
    assert image_paths[0].name == "DALL·E generated art.png"


def test_count_images(root_path: Path) -> None:
    """Check proper image counting."""
    assert count_images(root_path.joinpath("samples")) == 1


def test_resize_image(root_path, destination_image: Path) -> None:
    """Check that image gets resized."""
    source_image = root_path / SAMPLE_IMAGE_NAME_PATH
    resize_image(source_image, destination_image, max_size=300)
    with Image.open(destination_image) as test_result:
        assert test_result.width == 300
        assert test_result.height == 160
