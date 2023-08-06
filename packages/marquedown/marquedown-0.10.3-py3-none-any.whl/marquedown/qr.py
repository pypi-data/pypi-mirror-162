from __future__ import annotations

import re
import qrcode
from pathlib import Path
from itertools import count


RE_QR_INLINE = re.compile(r'\!\[qr\:(?P<alt>[^\n\s]+)\]\((?P<text>[^\n\s]+)\)')
RE_QR_MULTILINE = re.compile(r'\[o\] (?P<alt>.+)(?: \.*\[o\])?(?P<text>(?:\n\| .+)+)\n\[o\]$', re.MULTILINE)


class QRGenerator:
    """
    Generate QR codes

    Every image gets a unique index and it is increment for each.
    """

    def __init__(self, output_dir: Path, reference_dir: Path):
        self.output_dir = Path(output_dir)
        self.reference_dir = Path(reference_dir)

    def generate(self, text: str, alt: str) -> str:
        """
        Generate QR code from text.
        Saves image to file and returns HTML referencing the image.
        """

        # Get available filename
        image_name = self.get_available_filename(alt)
        
        # Generate and save image
        image = qrcode.make(text)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        image.save(self.output_dir / image_name)

        # Reference image and return HTML
        image_path = self.reference_dir / image_name
        return f'<img class="qr" src="{image_path!s}" alt="{alt}">'

    def get_available_filename(self, alt: str) -> str:
        """Increment an index until an available filename is found."""

        # Make alt valid for filename
        alt = re.sub(r'[^\w\d\-]+', '-', alt.lower())

        image_name = f'qr-{alt}.png'
        image_path = self.output_dir / image_name

        for i in count():
            if not image_path.exists():
                return image_name

            image_name = f'qr-{alt}-{i}.png'
            image_path = self.output_dir / image_name

    def repl_qr(self, match: re.Match) -> str:
        text, alt = match.group('text', 'alt')

        # Remove preceding pipelines at the beginning of lines
        text = " ".join([line.lstrip('| ') for line in text.split('\n')])
        # Replace `\n` in text with actual line breaks
        text = re.sub(r'\\n\s*', '\n', text)

        return self.generate(text, alt)


def qr(document: str, qrgen: QRGenerator) -> str:
    """
    Notation for QR codes

    QR code images will be generated and saved,
    and image elements inserted referencing their file locations.

    Example:
        Marquedown:
            ![qr:monero-wallet](monero:abcdefghijklmnopqrstuvwxyz)

            [o] Bee Movie transcript ..................[o]
            | According to all known laws of aviation,
            | there is no way that a bee should be able
            | to fly. Its wings are too small to get its
            | fat little body off the ground. The bee,
            | of course, flies anyway because bees don't
            | care what humans think is impossible.
            [o]

        HTML:
            <img src="qr/qr-monero-wallet.png" alt="monero-wallet">

            <img class="qr" src="qr/qr-bee-movie-transcript.png" alt="Bee Movie transcript">
    """

    document = RE_QR_MULTILINE.sub(qrgen.repl_qr, document)
    document = RE_QR_INLINE.sub(qrgen.repl_qr, document)

    return document