# Label maker

This script takes a PDF as an input, crops it to remove all whitespace, then
creates a new PDF with one of four fields populated with the scaled content of
the original PDF.  The original content will be rotated to fit if necessary.

The output PDF is scaled to fit the fields on an Avery 8168 label sheet.  I
use it to create printable stickers from eBay-generated mailing labels.

# Usage

```
usage: labelmaker.py [-h] input_pdf output_pdf {upper-left,upper-right,lower-left,lower-right,ul,ur,ll,lr}

Extract the visible content from the first page of a PDF, remove surrounding whitespace, optionally rotate it, and
place it into a selected field of a new 8.5 x 11 PDF.

positional arguments:
  input_pdf             Path to the input PDF
  output_pdf            Path to the output PDF
  {upper-left,upper-right,lower-left,lower-right,ul,ur,ll,lr}
                        Field in which to place the extracted image

options:
  -h, --help            show this help message and exit
```
