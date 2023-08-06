import re


RE_BBLIKE = re.compile(r'\[(\/*)([\w\d\.]*)(?:[ ]*\#([a-zA-Z][\w\d\-\_\:\.]*))?\](?!\(.*\))')


def _replace_segment(text: str, i: int, j: int, replacement: str):
    """Remove segment of text and insert a replacement."""
    return text[:i] + replacement + text[j:]


def bblike(document: str):
    """Notation for BBCode-like HTML tags.
    
    Marquedown:
        Hello, [.green]there[/]!
        How [b]are [i]you?[//]

    HTML:
        Hello, <div class="green">there</div>!
        How <b>are <i>you?</i></b>
    """

    # Keep track of opened tags
    stack = []

    # Offset is used to correct for the lengths
    # of previous replacements when replacing new matches
    offset = 0

    for m in list(RE_BBLIKE.finditer(document)):
        escapers = len(m.group(1))
        tag, *classes = m.group(2).split('.')
        id_ = m.group(3)

        if escapers > 0:
            elements = []
            
            while stack and escapers:
                last_tag = stack.pop()

                if tag == "" or last_tag == tag:
                    escapers -= 1

                # Generate HTML element and add to be appended
                elements.append(f'</{last_tag}>')

            # Insert elements at match
            replacement = "".join(elements)
            document = _replace_segment(document, m.start() + offset, m.end() + offset, replacement)

            # Adjust offset
            offset += len(replacement) - len(m.group(0))
        
        else:
            # Default tag is `div` for convenience
            if not tag:
                tag = 'div'
            
            # Generate HTML element
            element = f'<{tag}'

            if classes:
                element += f' class="{" ".join(classes)}"'

            if id_ is not None:
                element += f' id="{id_}"'

            element += '>'

            # Insert tag at match
            document = _replace_segment(document, m.start() + offset, m.end() + offset, element)

            # Adjust offset
            offset += len(element) - len(m.group(0))

            # Add as opened tag
            stack.append(tag)

    return document