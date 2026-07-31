#!/usr/bin/env python3
"""Compare equivalent PNG captures without third-party dependencies."""

from __future__ import annotations

import argparse
import binascii
import json
from pathlib import Path
import struct
import sys
from typing import Any
import zlib


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHANNELS_BY_COLOR_TYPE = {0: 1, 2: 3, 4: 2, 6: 4}


class PngInputError(ValueError):
    """Raised when a PNG cannot be compared by this bounded helper."""


def paeth(left: int, up: int, up_left: int) -> int:
    prediction = left + up - up_left
    left_distance = abs(prediction - left)
    up_distance = abs(prediction - up)
    up_left_distance = abs(prediction - up_left)
    if left_distance <= up_distance and left_distance <= up_left_distance:
        return left
    if up_distance <= up_left_distance:
        return up
    return up_left


def read_png(path: Path) -> tuple[int, int, list[tuple[int, int, int]]]:
    """Decode a deliberately small, screenshot-oriented subset of PNG."""

    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise PngInputError(f"{path}: not a PNG file")

    offset = len(PNG_SIGNATURE)
    header: tuple[int, int, int, int, int, int, int] | None = None
    compressed = bytearray()
    saw_end = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise PngInputError(f"{path}: truncated PNG chunk")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            raise PngInputError(f"{path}: truncated PNG chunk payload")
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack(
            ">I", data[offset + 8 + length : chunk_end]
        )[0]
        actual_crc = binascii.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise PngInputError(f"{path}: invalid {chunk_type!r} checksum")
        offset = chunk_end

        if chunk_type == b"IHDR":
            if header is not None or len(chunk_data) != 13:
                raise PngInputError(f"{path}: invalid IHDR")
            header = struct.unpack(">IIBBBBB", chunk_data)
        elif chunk_type == b"IDAT":
            compressed.extend(chunk_data)
        elif chunk_type == b"IEND":
            saw_end = True
            break

    if header is None:
        raise PngInputError(f"{path}: missing IHDR")
    if not saw_end:
        raise PngInputError(f"{path}: missing IEND")

    width, height, bit_depth, color_type, compression, filtering, interlace = header
    if width < 1 or height < 1:
        raise PngInputError(f"{path}: invalid dimensions {width}x{height}")
    if bit_depth != 8 or color_type not in CHANNELS_BY_COLOR_TYPE:
        raise PngInputError(
            f"{path}: only 8-bit grayscale, RGB, grayscale-alpha, and RGBA "
            "PNGs are supported"
        )
    if compression != 0 or filtering != 0 or interlace != 0:
        raise PngInputError(
            f"{path}: unsupported compression method, filter method, or interlace"
        )

    bytes_per_pixel = CHANNELS_BY_COLOR_TYPE[color_type]
    row_bytes = width * bytes_per_pixel
    try:
        raw = zlib.decompress(bytes(compressed))
    except zlib.error as exc:
        raise PngInputError(f"{path}: invalid compressed image data") from exc
    expected_size = height * (row_bytes + 1)
    if len(raw) != expected_size:
        raise PngInputError(
            f"{path}: decoded byte length {len(raw)} does not match {expected_size}"
        )

    pixels: list[tuple[int, int, int]] = []
    cursor = 0
    previous = bytearray(row_bytes)
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        encoded = raw[cursor : cursor + row_bytes]
        cursor += row_bytes
        decoded = bytearray(row_bytes)

        for index, value in enumerate(encoded):
            left = decoded[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            up = previous[index]
            up_left = (
                previous[index - bytes_per_pixel]
                if index >= bytes_per_pixel
                else 0
            )
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                predictor = paeth(left, up, up_left)
            else:
                raise PngInputError(f"{path}: unsupported row filter {filter_type}")
            decoded[index] = (value + predictor) & 0xFF

        for sample_offset in range(0, len(decoded), bytes_per_pixel):
            sample = decoded[sample_offset : sample_offset + bytes_per_pixel]
            if color_type == 0:
                red = green = blue = sample[0]
                alpha = 255
            elif color_type == 2:
                red, green, blue = sample
                alpha = 255
            elif color_type == 4:
                red = green = blue = sample[0]
                alpha = sample[1]
            else:
                red, green, blue, alpha = sample
            if alpha != 255:
                red = (red * alpha + 255 * (255 - alpha) + 127) // 255
                green = (green * alpha + 255 * (255 - alpha) + 127) // 255
                blue = (blue * alpha + 255 * (255 - alpha) + 127) // 255
            pixels.append((red, green, blue))

        previous = decoded

    return width, height, pixels


def png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    checksum = binascii.crc32(chunk_type + payload) & 0xFFFFFFFF
    return (
        struct.pack(">I", len(payload))
        + chunk_type
        + payload
        + struct.pack(">I", checksum)
    )


def write_rgb_png(
    path: Path,
    width: int,
    height: int,
    pixels: list[tuple[int, int, int]],
) -> None:
    rows = bytearray()
    for y_position in range(height):
        rows.append(0)
        start = y_position * width
        for red, green, blue in pixels[start : start + width]:
            rows.extend((red, green, blue))

    output = bytearray(PNG_SIGNATURE)
    output.extend(
        png_chunk(
            b"IHDR",
            struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0),
        )
    )
    output.extend(png_chunk(b"IDAT", zlib.compress(bytes(rows), level=9)))
    output.extend(png_chunk(b"IEND", b""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(output)


def as_percent(value: float) -> float:
    return round(value * 100, 3)


def compare(
    reference_path: Path,
    candidate_path: Path,
    *,
    tolerance: int = 16,
    grid_columns: int = 4,
    grid_rows: int = 4,
    heatmap_path: Path | None = None,
) -> dict[str, Any]:
    if not 0 <= tolerance <= 255:
        raise PngInputError("tolerance must be from 0 through 255")
    if grid_columns < 1 or grid_rows < 1:
        raise PngInputError("grid dimensions must be positive")

    ref_width, ref_height, reference = read_png(reference_path)
    cand_width, cand_height, candidate = read_png(candidate_path)
    if (ref_width, ref_height) != (cand_width, cand_height):
        raise PngInputError(
            "image dimensions differ: "
            f"reference={ref_width}x{ref_height}, "
            f"candidate={cand_width}x{cand_height}"
        )
    if grid_columns > ref_width or grid_rows > ref_height:
        raise PngInputError(
            "grid dimensions cannot exceed the image dimensions: "
            f"grid={grid_columns}x{grid_rows}, image={ref_width}x{ref_height}"
        )

    total_pixels = ref_width * ref_height
    changed = 0
    severe = 0
    total_channel_delta = 0
    changed_bounds = [ref_width, ref_height, -1, -1]
    cell_stats = [
        {"pixels": 0, "changed": 0, "delta": 0}
        for _ in range(grid_columns * grid_rows)
    ]
    heatmap: list[tuple[int, int, int]] = []

    for index, (ref_pixel, cand_pixel) in enumerate(zip(reference, candidate)):
        x_position = index % ref_width
        y_position = index // ref_width
        deltas = tuple(
            abs(ref_channel - cand_channel)
            for ref_channel, cand_channel in zip(ref_pixel, cand_pixel)
        )
        max_delta = max(deltas)
        channel_delta = sum(deltas)
        total_channel_delta += channel_delta
        is_changed = max_delta > tolerance
        if is_changed:
            changed += 1
            changed_bounds[0] = min(changed_bounds[0], x_position)
            changed_bounds[1] = min(changed_bounds[1], y_position)
            changed_bounds[2] = max(changed_bounds[2], x_position)
            changed_bounds[3] = max(changed_bounds[3], y_position)
        if max_delta > max(64, tolerance):
            severe += 1

        column = min(grid_columns - 1, x_position * grid_columns // ref_width)
        row = min(grid_rows - 1, y_position * grid_rows // ref_height)
        cell = cell_stats[row * grid_columns + column]
        cell["pixels"] += 1
        cell["changed"] += int(is_changed)
        cell["delta"] += channel_delta

        if heatmap_path is not None:
            gray = round(
                cand_pixel[0] * 0.2126
                + cand_pixel[1] * 0.7152
                + cand_pixel[2] * 0.0722
            )
            if is_changed:
                intensity = max_delta / 255
                heatmap.append(
                    (
                        255,
                        round((1 - intensity) * min(210, gray)),
                        round((1 - intensity) * min(210, gray)),
                    )
                )
            else:
                faded = round(225 + gray * 0.1)
                heatmap.append((faded, faded, faded))

    bounds: dict[str, int] | None
    if changed:
        x_start, y_start, x_end, y_end = changed_bounds
        bounds = {
            "x": x_start,
            "y": y_start,
            "width": x_end - x_start + 1,
            "height": y_end - y_start + 1,
        }
    else:
        bounds = None

    hotspots: list[dict[str, int | float]] = []
    for index, cell in enumerate(cell_stats):
        pixels = cell["pixels"]
        changed_pixels = cell["changed"]
        mean_delta = cell["delta"] / (pixels * 3)
        hotspots.append(
            {
                "column": index % grid_columns,
                "row": index // grid_columns,
                "changed_pixel_percent": as_percent(changed_pixels / pixels),
                "mean_channel_delta": round(mean_delta, 3),
                "severity": round((changed_pixels / pixels) * mean_delta, 3),
            }
        )
    hotspots.sort(key=lambda item: float(item["severity"]), reverse=True)

    if heatmap_path is not None:
        write_rgb_png(heatmap_path, ref_width, ref_height, heatmap)

    mean_channel_delta = total_channel_delta / (total_pixels * 3)
    return {
        "method": "max_rgb_channel_delta",
        "reference_path": str(reference_path),
        "candidate_path": str(candidate_path),
        "dimensions": {"width": ref_width, "height": ref_height},
        "tolerance": tolerance,
        "pixel_similarity_percent": as_percent(1 - changed / total_pixels),
        "changed_pixel_percent": as_percent(changed / total_pixels),
        "severe_pixel_percent": as_percent(severe / total_pixels),
        "mean_absolute_channel_error": round(mean_channel_delta, 3),
        "mean_color_similarity_percent": as_percent(
            1 - mean_channel_delta / 255
        ),
        "changed_bounds": bounds,
        "grid": {"columns": grid_columns, "rows": grid_rows},
        "hotspots": hotspots[: min(8, len(hotspots))],
        "heatmap_path": str(heatmap_path) if heatmap_path is not None else None,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare equivalent PNG captures and emit secondary localization "
            "evidence. This metric is not a semantic visual pass gate."
        )
    )
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--tolerance", type=int, default=16)
    parser.add_argument("--grid-columns", type=int, default=4)
    parser.add_argument("--grid-rows", type=int, default=4)
    parser.add_argument("--heatmap", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = compare(
            args.reference,
            args.candidate,
            tolerance=args.tolerance,
            grid_columns=args.grid_columns,
            grid_rows=args.grid_rows,
            heatmap_path=args.heatmap,
        )
    except (OSError, PngInputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
