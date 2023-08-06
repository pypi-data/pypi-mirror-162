import re

from . import marquedown as mqd
from .tagtools import tagstrip, contained


RE_LABELLIST = re.compile(r'^(?:(?P<class>[^\s\n]+)\:\n)?(?P<labels>(?:\(\|[ ]+[\w\d\-\_\:\.]+\:[ ]+.+(?:\n|$))+)', re.MULTILINE)
RE_LABEL = re.compile(r'^\(\|[ ]+([\w\d\-\_\:\.]+)\:[ ]+(.+)$')


def _repl_labellist(match: re.Match):
    # Extract label name and content from each line
    labels = []
    
    for line in match.group('labels').splitlines():
        m = RE_LABEL.match(line)

        if not m:
            raise RuntimeError(
                'Line in label list is not a label. '
                'This error should be impossible to occur.')

        name, content = m.group(1, 2)

        # Parse Marquedown in content
        parsed_content = mqd(content)
        
        # Strip added paragraph tags
        if not contained(content, 'p'):
            parsed_content = tagstrip(parsed_content, 'p')

        labels.append((name, parsed_content))

    # Render list items
    rendered_labels = "\n".join(
        f'<li class="label label-{name}">{content}</li>'
        for name, content in labels)

    # And finally, render the label list

    _class = match.group('class')
    if _class is not None:
        # Add class to list if one is provided
        return f'<ul class="labels {_class}">\n{rendered_labels}\n</ul>'
    else:
        return f'<ul class="labels">\n{rendered_labels}\n</ul>'


def labellist(document: str):
    """Notation for label lists.
    
    Marquedown:
        (| email: [jon@webby.net](mailto:jon@webby.net)
        (| matrix: [@jon:webby.net](https://matrix.to/#/@jon:webby.net)
        (| runescape: jonathan_superstar1777

    HTML:
        <ul class="labels">
            <li class="label-email">
                <a href="mailto:jon@webby.net">
                    jon@webby.net
                </a>
            </li>
            <li class="label-matrix">
                <a href="https://matrix.to/#/@jon:webby.net">
                    @jon:webby.net
                </a>
            </li>
            <li class="label-runescape">
                jonathan_superstar1777
            </li>
        </ul>
    """

    return RE_LABELLIST.sub(_repl_labellist, document)