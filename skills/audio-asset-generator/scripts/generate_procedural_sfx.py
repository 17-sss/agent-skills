#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44100
PRESETS = ("ui-click", "success", "error", "pickup", "whoosh", "impact", "portal")


def clamp(v: float) -> float:
    return max(-1.0, min(1.0, v))


def env(t: float, duration: float, attack: float = 0.01, release: float = 0.08) -> float:
    a = min(1.0, t / max(attack, 1e-6))
    r = min(1.0, (duration - t) / max(release, 1e-6))
    return max(0.0, min(a, r))


def osc(freq: float, t: float, kind: str = "sine") -> float:
    phase = 2.0 * math.pi * freq * t
    if kind == "sine":
        return math.sin(phase)
    if kind == "square":
        return 1.0 if math.sin(phase) >= 0 else -1.0
    if kind == "triangle":
        return (2.0 / math.pi) * math.asin(math.sin(phase))
    raise ValueError(kind)


def render(preset: str, seed: int) -> list[float]:
    rng = random.Random(seed)
    pitch_scale = rng.uniform(0.96, 1.04)
    texture_scale = rng.uniform(0.92, 1.08)
    durations = {
        "ui-click": 0.09,
        "success": 0.34,
        "error": 0.28,
        "pickup": 0.24,
        "whoosh": 0.42,
        "impact": 0.30,
        "portal": 0.80,
    }
    duration = durations[preset]
    count = int(SAMPLE_RATE * duration)
    out: list[float] = []

    for i in range(count):
        t = i / SAMPLE_RATE
        e = env(t, duration, attack=0.004, release=min(0.16, duration * 0.45))
        n = rng.uniform(-1.0, 1.0)

        if preset == "ui-click":
            v = 0.65 * osc((1300 - 450 * (t / duration)) * pitch_scale, t) + 0.18 * n
            v *= e * math.exp(-18 * t)
        elif preset == "success":
            f = (660 if t < duration / 2 else 990) * pitch_scale
            v = 0.55 * osc(f, t, "sine") + 0.15 * texture_scale * osc(f * 2, t, "triangle")
            v *= e
        elif preset == "error":
            f = (240 - 70 * (t / duration)) * pitch_scale
            v = 0.55 * osc(f, t, "square") + 0.12 * n
            v *= e
        elif preset == "pickup":
            f = (700 + 1100 * (t / duration)) * pitch_scale
            v = 0.52 * osc(f, t) + 0.12 * texture_scale * osc(f * 2, t)
            v *= e
        elif preset == "whoosh":
            sweep = math.sin(math.pi * min(1.0, t / duration))
            v = n * (0.18 + 0.72 * sweep)
            v *= e
        elif preset == "impact":
            f = (105 - 60 * (t / duration)) * pitch_scale
            low = osc(max(35, f), t)
            v = 0.65 * low + 0.55 * n * math.exp(-20 * t)
            v *= e * math.exp(-5 * t)
        elif preset == "portal":
            f = (180 + 420 * (t / duration)) * pitch_scale
            wobble = 1.0 + 0.05 * math.sin(2 * math.pi * 7 * t)
            v = (
                0.38 * osc(f * wobble, t)
                + 0.24 * texture_scale * osc(f * 1.5, t)
                + 0.16 * n
            )
            v *= e * (0.65 + 0.35 * math.sin(math.pi * t / duration))
        else:
            raise ValueError(preset)

        out.append(clamp(v * 0.85))

    peak = max((abs(v) for v in out), default=1.0)
    gain = 0.92 / peak if peak > 0 else 1.0
    return [clamp(v * gain) for v in out]


def write_wav(path: Path, samples: list[float], *, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if overwrite else "xb"
    with path.open(mode) as output:
        with wave.open(output, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            frames = b"".join(struct.pack("<h", int(clamp(v) * 32767)) for v in samples)
            wav.writeframes(frames)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate small dependency-free procedural WAV sound effects.")
    parser.add_argument("--preset", choices=PRESETS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--force", action="store_true", help="Replace an existing output file.")
    parser.add_argument("--list-presets", action="store_true")
    args = parser.parse_args()

    if args.list_presets:
        print("\n".join(PRESETS))
        return 0
    if not args.preset or not args.output:
        parser.error("--preset and --output are required unless --list-presets is used")

    try:
        write_wav(args.output, render(args.preset, args.seed), overwrite=args.force)
    except FileExistsError:
        parser.error(f"output already exists: {args.output}; pass --force to replace it")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
