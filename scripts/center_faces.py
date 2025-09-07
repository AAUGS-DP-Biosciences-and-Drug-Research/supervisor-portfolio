#!/usr/bin/env python3
"""Center faces in images based on manual coordinates.

The script reads a YAML file mapping image filenames to the ``x``/``y``
coordinates of the face center. Each matching image is cropped to a square
region centered on those coordinates. Images missing from the YAML file are
simply cropped around their own center.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple

import yaml
from PIL import Image


def load_centers(path: Path) -> Dict[str, Tuple[int, int]]:
    """Load a mapping of filenames to ``(x, y)`` centers from ``path``."""
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text()) or {}
    centers: Dict[str, Tuple[int, int]] = {}
    for name, coords in data.items():
        if isinstance(coords, dict) and "x" in coords and "y" in coords:
            centers[name] = (int(coords["x"]), int(coords["y"]))
    return centers


def center_image(image_path: Path, center: Tuple[int, int] | None) -> None:
    """Crop ``image_path`` to a square around ``center`` in-place."""
    with Image.open(image_path) as img:
        width, height = img.size
        cx = center[0] if center else width // 2
        cy = center[1] if center else height // 2
        side = min(width, height)
        left = max(min(cx - side // 2, width - side), 0)
        top = max(min(cy - side // 2, height - side), 0)
        img.crop((left, top, left + side, top + side)).save(image_path)


def process_folder(folder: Path, centers: Dict[str, Tuple[int, int]]) -> None:
    for path in folder.iterdir():
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            center_image(path, centers.get(path.name))


def main() -> None:
    parser = argparse.ArgumentParser(description="Center faces within images")
    parser.add_argument("folder", type=Path, help="Folder containing images")
    parser.add_argument(
        "--centers",
        type=Path,
        default=Path("data/face_centers.yaml"),
        help="YAML file mapping filenames to face centers",
    )
    args = parser.parse_args()
    centers = load_centers(args.centers)
    process_folder(args.folder, centers)


if __name__ == "__main__":
    main()
