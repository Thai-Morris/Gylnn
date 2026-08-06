"""Generate the site's favicon set from the cropped RM logo artwork."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


PAPER = (243, 242, 236, 255)


def remove_white_background(image: Image.Image) -> Image.Image:
    """Remove the white matte while retaining antialiased logo edges."""
    rgb = image.convert("RGB")
    output = Image.new("RGBA", rgb.size)
    converted: list[tuple[int, int, int, int]] = []

    pixels = rgb.load()
    for y in range(rgb.height):
        for x in range(rgb.width):
            red, green, blue = pixels[x, y]
            distance = max(255 - red, 255 - green, 255 - blue)

            if distance <= 3:
                converted.append((255, 255, 255, 0))
                continue

            alpha = 255 if distance >= 236 else round((distance - 3) * 255 / 233)

            def unmatte(channel: int) -> int:
                value = 255 + (channel - 255) * 255 / alpha
                return max(0, min(255, round(value)))

            converted.append((unmatte(red), unmatte(green), unmatte(blue), alpha))

    output.putdata(converted)
    bounds = output.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("The source image does not contain visible logo artwork.")
    return output.crop(bounds)


def render_square(
    artwork: Image.Image,
    size: int,
    *,
    background: tuple[int, int, int, int] = (255, 255, 255, 0),
    horizontal_padding: float = 0.045,
) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), background)
    available_width = max(1, round(size * (1 - 2 * horizontal_padding)))
    scale = available_width / artwork.width
    rendered_size = (
        available_width,
        max(1, round(artwork.height * scale)),
    )
    rendered = artwork.resize(rendered_size, Image.Resampling.LANCZOS)
    position = (
        (size - rendered.width) // 2,
        (size - rendered.height) // 2,
    )
    canvas.alpha_composite(rendered, position)
    return canvas


def generate(source: Path, output_dir: Path, navbar_output: Path | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artwork = remove_white_background(Image.open(source))
    tail_crop = round(artwork.width * 0.10)
    artwork = artwork.crop((tail_crop, 0, artwork.width - tail_crop, artwork.height))

    if navbar_output is not None:
        navbar_output.parent.mkdir(parents=True, exist_ok=True)
        artwork.save(navbar_output, optimize=True)

    transparent_icons: dict[int, Image.Image] = {}
    for size in (16, 32, 48):
        icon = render_square(artwork, size)
        transparent_icons[size] = icon
        icon.save(output_dir / f"favicon-{size}x{size}.png", optimize=True)

    transparent_icons[48].save(
        output_dir / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=[transparent_icons[32], transparent_icons[16]],
    )

    render_square(artwork, 180, background=PAPER, horizontal_padding=0.07).save(
        output_dir / "apple-touch-icon.png",
        optimize=True,
    )

    for size in (192, 512):
        render_square(artwork, size, background=PAPER, horizontal_padding=0.07).save(
            output_dir / f"android-chrome-{size}x{size}.png",
            optimize=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--navbar-output", type=Path)
    args = parser.parse_args()
    generate(args.source, args.output_dir, args.navbar_output)


if __name__ == "__main__":
    main()
