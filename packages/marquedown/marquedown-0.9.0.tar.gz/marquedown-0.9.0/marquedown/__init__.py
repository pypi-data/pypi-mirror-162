__version__ = '0.9.0'

import markdown as md


def marquedown(document: str, **kwargs):
    """Convert both Marquedown and Markdown into HTML."""

    if kwargs.get('citation', True):
        from .citation import citation
        document = citation(document)

    if kwargs.get('video', True):
        from .video import video
        document = video(document)

    if kwargs.get('labellist', True):
        from .labellist import labellist
        document = labellist(document)

    # Parse QR codes
    # with provided QRGenerator
    if kwargs.get('qrgen') is not None: 
        from .qr import QRGenerator
        qrgen = kwargs.get('qrgen')

        if isinstance(qrgen, str):
            qrgen = QRGenerator.from_paths(qrgen)

        # Parse QR codes
        from .qr import qr
        document = qr(document, qrgen)
        
    html = md.markdown(document)

    if kwargs.get('bblike', True):
        from .bblike import bblike
        html = bblike(html)

    return html