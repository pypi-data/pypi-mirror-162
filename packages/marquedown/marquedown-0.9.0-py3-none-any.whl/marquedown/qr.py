from __future__ import annotations

import re
import qrcode
from pathlib import Path


RE_QR = re.compile(r'\!\[qr\:(?P<alt>[^\n\s]+)\]\((?P<text>[^\n\s]+)\)')


class QRGenerator:
    def __init__(self, save_dir: Path, reference_dir: Path):
        self.save_dir = Path(save_dir)
        self.reference_dir = Path(reference_dir)
        self.image_index = 0

    @classmethod
    def from_paths(cls, paths: str) -> QRGenerator:
        """
        Split string into two paths
            1. Where to save generated QR codes
            2. Directory to reference the images
        """
        save_dir, reference_dir = paths.split(':')

        save_dir = Path(save_dir)
        reference_dir = Path(reference_dir)

        return QRGenerator(save_dir, reference_dir)

    def repl_qr(self, match: re.Match) -> str:
        text, alt = match.group('text', 'alt')

        # Get image name by index
        image_name = f'qr-{self.image_index}-{alt}.png'
        self.image_index += 1
        
        # Generate image from text
        image = qrcode.make(text)

        # Save image
        self.save_dir.mkdir(parents=True, exist_ok=True)
        image.save(self.save_dir / image_name)

        # Reference image and return HTML
        image_path = self.reference_dir / image_name
        return f'<img src="{image_path!s}" alt="{alt}">'


def qr(document: str, qrgen: QRGenerator) -> str:
    """
    Notation for QR codes

    QR code images will be generated and saved,
    and image elements inserted referencing their file locations.


    Example:
        Saving images to `public/imgs/qr`
        Referencing them relative to `/imgs/qr`

        Marquedown:
            ![qr:monero](monero:abcdefhijklmnopqrstuvwxyz)
            ![qr:dimweb](https://youtu.be/VmAEkV5AYSQ)

        HTML:
            <img src="/imgs/qr/qr-0.png" alt="monero">
            <img src="/imgs/qr/qr-1.png" alt="dimweb">
    """

    document = RE_QR.sub(qrgen.repl_qr, document)

    return document