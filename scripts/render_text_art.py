#!/usr/bin/env python3
"""Render a poem-only typographic scene from an explicit JSON layout."""

from __future__ import annotations

import argparse
import json
import math
import random
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def rgb(value: str) -> tuple[int, int, int]:
    value = value.removeprefix("#")
    if len(value) != 6:
        raise ValueError(f"Expected six-digit hex color, got {value!r}")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def source_chars(lines: list[str]) -> set[str]:
    return {ch for line in lines for ch in line
            if not ch.isspace() and not unicodedata.category(ch).startswith("P")}


class Canvas:
    def __init__(self, spec: dict, font_path: str):
        self.lines = spec["poem"]["lines"]
        self.allowed = source_chars(self.lines)
        width, height = spec.get("size", [1200, 1600])
        self.width, self.height = int(width), int(height)
        if min(width, height) < 300:
            raise ValueError("Canvas is too small")
        self.palette = {key: rgb(value) for key, value in spec["palette"].items()}
        self.image = Image.new("RGB", (self.width, self.height),
                               self.palette["background"])
        self.font_path = font_path
        self.font_cache: dict[int, ImageFont.FreeTypeFont] = {}

    def font(self, size: int) -> ImageFont.FreeTypeFont:
        size = max(8, int(size))
        if size not in self.font_cache:
            self.font_cache[size] = ImageFont.truetype(self.font_path, size)
        return self.font_cache[size]

    def color(self, name: str) -> tuple[int, int, int]:
        if name not in self.palette:
            raise ValueError(f"Unknown palette color: {name}")
        return self.palette[name]

    def glyph(self, ch: str, x: float, y: float, size: int,
              color="ink", opacity=255, angle=0):
        if ch not in self.allowed:
            raise ValueError(f"Scene character {ch!r} is absent from the poem")
        size = max(8, int(size))
        padding = size * 2
        layer = Image.new("RGBA", (size + padding * 2, size + padding * 2))
        draw = ImageDraw.Draw(layer)
        draw.text((layer.width / 2, layer.height / 2), ch,
                  font=self.font(size), anchor="mm",
                  fill=(*self.color(color), int(opacity)))
        if angle:
            layer = layer.rotate(-float(angle), Image.Resampling.BICUBIC,
                                 expand=True)
        self.image.paste(layer, (int(x - layer.width / 2),
                                 int(y - layer.height / 2)), layer)

    def sequence(self, text: str, points: list[tuple[float, float]], size: int,
                 color="ink", opacity=255, rotate=False):
        if not text:
            return
        kept = []
        for point in points:
            if not kept or math.dist(point, kept[-1]) >= size * .82:
                kept.append(point)
        for index, (x, y) in enumerate(kept):
            angle = 0
            if rotate and len(kept) > 1:
                before = kept[max(0, index - 1)]
                after = kept[min(len(kept) - 1, index + 1)]
                angle = math.degrees(math.atan2(after[1] - before[1],
                                                after[0] - before[0]))
            self.glyph(text[index % len(text)], x, y, size, color,
                       opacity, angle)

    def element(self, item: dict):
        kind = item["type"]
        text = item["text"]
        for ch in text:
            if ch not in self.allowed:
                raise ValueError(f"Scene character {ch!r} is absent from the poem")
        size = int(item.get("size", 35))
        color = item.get("color", "ink")
        opacity = int(item.get("opacity", 255))
        if kind == "text":
            x, y = item["at"]
            step = float(item.get("step", size * 1.15))
            vertical = item.get("vertical", False)
            for index, ch in enumerate(text):
                self.glyph(ch, x + (0 if vertical else index * step),
                           y + (index * step if vertical else 0),
                           size, color, opacity)
        elif kind == "curve":
            p0, p1, p2 = item["points"]
            count = max(2, int(item.get("count", 30)))
            points = []
            for index in range(count):
                t = index / (count - 1)
                points.append(((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
                               (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]))
            self.sequence(text, points, size, color, opacity,
                          item.get("rotate", False))
        elif kind == "ellipse":
            cx, cy = item["center"]
            rx, ry = item["radii"]
            count = max(2, int(item.get("count", 32)))
            start = math.radians(float(item.get("start_deg", 0)))
            end = math.radians(float(item.get("end_deg", 360)))
            points = [(cx + rx * math.cos(start + (end-start)*i/(count-1)),
                       cy + ry * math.sin(start + (end-start)*i/(count-1)))
                      for i in range(count)]
            self.sequence(text, points, size, color, opacity)
        elif kind == "scatter":
            x0, y0, x1, y1 = item["box"]
            rng = random.Random(int(item.get("seed", 0)))
            for index in range(int(item.get("count", 30))):
                self.glyph(text[index % len(text)], rng.uniform(x0, x1),
                           rng.uniform(y0, y1), size, color, opacity)
        elif kind == "mountain":
            x0, x1 = item["x_range"]
            peak_x, peak_y = item["peak"]
            base_y = item["base_y"]
            step = int(item.get("step", size * 1.25))
            index = 0
            for row, y in enumerate(range(int(peak_y), int(base_y), step)):
                t = (y - peak_y) / (base_y - peak_y)
                left = peak_x + (x0 - peak_x) * t
                right = peak_x + (x1 - peak_x) * t
                x = left + (step / 2 if row % 2 else 0)
                while x <= right:
                    self.glyph(text[index % len(text)], x, y, size,
                               color, opacity)
                    index += 1
                    x += step
        else:
            raise ValueError(f"Unknown element type: {kind}")

    def reading_area(self, spec: dict):
        top = int(spec.get("top", self.height * .79))
        bottom = int(spec.get("bottom", self.height * .95))
        if not (0 <= top < bottom <= self.height):
            raise ValueError("Invalid reading area")
        rows = len(self.lines)
        line_step = (bottom - top) / max(rows, 1)
        for row, line in enumerate(self.lines):
            chars = [ch for ch in line if not ch.isspace()]
            if not chars:
                continue
            max_size = min(48, int(line_step * .74),
                           int(self.width * .78 / len(chars)))
            step = max_size * 1.18
            x0 = (self.width - (len(chars)-1)*step) / 2
            for col, ch in enumerate(chars):
                if ch in self.allowed:
                    self.glyph(ch, x0 + col*step, top + row*line_step,
                               max_size, "ink", 245)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("layout", type=Path)
    parser.add_argument("--font", required=True,
                        help="Path to a CJK font (.ttf, .otf, or .ttc)")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(args.layout.read_text(encoding="utf-8"))
    if not isinstance(spec["poem"]["lines"], list) or not spec["poem"]["lines"]:
        raise ValueError("poem.lines must be a non-empty list")
    canvas = Canvas(spec, args.font)
    for element in spec["elements"]:
        canvas.element(element)
    canvas.reading_area(spec.get("reading_area", {}))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.image.save(args.output, optimize=True)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
