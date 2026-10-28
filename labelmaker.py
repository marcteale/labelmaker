#!/usr/bin/env python3
import argparse
import io

import pymupdf
from PIL import Image, ImageChops


# --------------------------------------------------
# Constants
# --------------------------------------------------

PAGE_WIDTH = 8.5 * 72       # 612 points
PAGE_HEIGHT = 11 * 72       # 792 points
MARGIN = 0.5 * 72           # 36 points

FIELD_WIDTH = 3.5 * 72      # 252 points
FIELD_HEIGHT = 5 * 72       # 360 points
DIVIDER_WIDTH = 0.5 * 72    # 36 points


# --------------------------------------------------
# Field positions
# --------------------------------------------------

FIELDS = {
    "upper-left": pymupdf.Rect(
        MARGIN,
        MARGIN,
        MARGIN + FIELD_WIDTH,
        MARGIN + FIELD_HEIGHT,
    ),

    "upper-right": pymupdf.Rect(
        MARGIN + FIELD_WIDTH + DIVIDER_WIDTH,
        MARGIN,
        MARGIN + FIELD_WIDTH + DIVIDER_WIDTH + FIELD_WIDTH,
        MARGIN + FIELD_HEIGHT,
    ),

    "lower-left": pymupdf.Rect(
        MARGIN,
        MARGIN + FIELD_HEIGHT,
        MARGIN + FIELD_WIDTH,
        MARGIN + FIELD_HEIGHT + FIELD_HEIGHT,
    ),

    "lower-right": pymupdf.Rect(
        MARGIN + FIELD_WIDTH + DIVIDER_WIDTH,
        MARGIN + FIELD_HEIGHT,
        MARGIN + FIELD_WIDTH + DIVIDER_WIDTH + FIELD_WIDTH,
        MARGIN + FIELD_HEIGHT + FIELD_HEIGHT,
    ),
}


# --------------------------------------------------
# Parse command-line arguments
# --------------------------------------------------

parser = argparse.ArgumentParser(
    description=(
        "Extract the visible content from the first page of a PDF, "
        "remove surrounding whitespace, optionally rotate it, and "
        "place it into a selected field of a new 8.5 x 11 PDF."
    )
)

parser.add_argument(
    "input_pdf",
    help="Path to the input PDF",
)

parser.add_argument(
    "output_pdf",
    help="Path to the output PDF",
)

parser.add_argument(
    "field",
    choices=FIELDS.keys(),
    help="Field in which to place the extracted image",
)

args = parser.parse_args()


# --------------------------------------------------
# Open and render the source PDF
# --------------------------------------------------

source = pymupdf.open(args.input_pdf)

if len(source) == 0:
    source.close()
    raise RuntimeError("The input PDF contains no pages.")

source_page = source[0]

# Render at 2x resolution for better image quality
pix = source_page.get_pixmap(
    matrix=pymupdf.Matrix(2, 2),
    alpha=False,
)

# Convert the rendered page to a PIL image
image = Image.frombytes(
    "RGB",
    [pix.width, pix.height],
    pix.samples,
)

source.close()


# --------------------------------------------------
# Remove surrounding whitespace
# --------------------------------------------------

background = Image.new("RGB", image.size, "white")

diff = ImageChops.difference(image, background)

bbox = diff.getbbox()

if bbox is None:
    raise RuntimeError(
        "The first page of the input PDF appears to be completely white."
    )

cropped = image.crop(bbox)


# --------------------------------------------------
# Rotate landscape images 90 degrees
# --------------------------------------------------

if cropped.width > cropped.height:
    cropped = cropped.transpose(Image.Transpose.ROTATE_90)


# --------------------------------------------------
# Convert image to PNG bytes
# --------------------------------------------------

image_buffer = io.BytesIO()

cropped.save(
    image_buffer,
    format="PNG",
)

image_buffer.seek(0)


# --------------------------------------------------
# Create the new PDF
# --------------------------------------------------

output = pymupdf.open()

page = output.new_page(
    width=PAGE_WIDTH,
    height=PAGE_HEIGHT,
)


# --------------------------------------------------
# Determine selected field
# --------------------------------------------------

field_rect = FIELDS[args.field]


# --------------------------------------------------
# Scale image to fit inside selected field
# --------------------------------------------------

image_width, image_height = cropped.size

field_width = field_rect.width
field_height = field_rect.height

scale = min(
    field_width / image_width,
    field_height / image_height,
)

display_width = image_width * scale
display_height = image_height * scale


# Center image within the selected field

x = field_rect.x0 + (
    field_width - display_width
) / 2

y = field_rect.y0 + (
    field_height - display_height
) / 2

image_rect = pymupdf.Rect(
    x,
    y,
    x + display_width,
    y + display_height,
)


# --------------------------------------------------
# Insert image
# --------------------------------------------------

page.insert_image(
    image_rect,
    stream=image_buffer.getvalue(),
)


# --------------------------------------------------
# Save output PDF
# --------------------------------------------------

output.save(args.output_pdf)
output.close()


print(f"Created: {args.output_pdf}")
print(f"Field:   {args.field}")
