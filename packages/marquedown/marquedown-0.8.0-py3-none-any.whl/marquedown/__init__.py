__version__ = '0.8.0'

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
        
    html = md.markdown(document)

    if kwargs.get('bblike', True):
        from .bblike import bblike
        html = bblike(html)

    return html