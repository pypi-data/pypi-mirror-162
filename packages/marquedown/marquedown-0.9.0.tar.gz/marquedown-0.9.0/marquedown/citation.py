import re

from . import marquedown as mqd


RE_CITATION = re.compile(r'^(?:\.+\n)?((?:\>.*\n)+)(?:\n?\-{2}[ ](.+)\n?)?(?:\'+)?', flags=re.MULTILINE)


def _repl_citation(match: re.Match):
    quote, source = match.group(1, 2)

    # Remove angle brackets in quote
    quote = '\n'.join(line[1:].lstrip() for line in quote.splitlines())

    # Parse Marquedown in quote
    quote = mqd(quote)

    # Include source if provided
    if source is not None:
        # Parse Marquedown in source
        source = mqd(source)

        # Remove surrounding paragraph from source
        if source.startswith('<p>') and source.endswith('</p>'):
            source = source[3:-4]

        # Put everything into HTML
        return f'<blockquote>\n{quote}\n<cite>{source}</cite>\n</blockquote>'

    # Exclude source if not provided
    return f'<blockquote>\n{quote}\n</blockquote>'


def citation(document: str):
    """Notation for blockquotes that include citation.

    Marquedown:
        ......................................................
        > You have enemies? Good. That means you've stood up
        > for something, sometime in your life.
        -- Winston Churchill
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''

    HTML:
        <blockquote>
            <p>
                You have enemies? Good. That means you've stood up
                for something, sometime in your life.
            </p>
            <cite>Winston Churchill</cite>
        </blockquote>
    """

    return RE_CITATION.sub(_repl_citation, document)