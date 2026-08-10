"""Conservatively minify the site's CSS without external dependencies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def minify(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    css = re.sub(r"\s+", " ", css).strip()
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)
    css = css.replace(";}", "}")
    return css


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source = args.source.read_text(encoding="utf-8")
    args.output.write_text(minify(source), encoding="utf-8", newline="")


if __name__ == "__main__":
    main()
