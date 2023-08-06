# Render all Markdown and Marquedown documents
# from a specified directory and all its subdirectories.
# 
# Provide a template for embedding the rendered content.

import re
import os
import yaml

from typing import Any
from pathlib import Path
from collections import defaultdict

from .. import marquedown


def extract_metadata(document: str):
    """Extract metadata from a YAML code block at the top of the document.
    
    Example:
        ```yml
        title: Page Title
        ```
    """

    m = re.search(r'^\`{3}ya?ml\n((?:.|\n)*?)\n\`{3}\s+', document)

    # Return without metadata if missing
    if not m:
        return {}, document

    # Remove metadata from document
    document = document[len(m.group(0)):]

    # Attempt to load metadata from YAML
    metadata = yaml.safe_load(m.group(1)) or {}

    if not isinstance(metadata, dict):
        raise ValueError('Metadata must be a dictionary.')

    return metadata, document


def find_documents(source: Path, destination: Path):
    """Locate all Marquedown documents in the source directory and its subdirectories.
    Yields the source of every document, and the destination for its `index.html`.
    """

    for directory, _, filenames in os.walk(source):
        for fname in filenames:
            file_source = Path(directory) / fname

            if not file_source.is_file():
                continue
            if file_source.suffix not in ('.md', '.mqd'):
                continue

            # File destination from relative path without suffix
            file_relative_path = file_source.relative_to(source)
            file_relative_path = str(file_relative_path)[:-len(file_relative_path.suffix)]
            file_destination = destination / file_relative_path

            # Don't use document name if it is `index.md` or `index.mqd`
            # This should be equivalent to how `index.html` works and be hidden

            if file_source.name in ('index.md', 'index.mqd'):
                yield file_source, file_destination.parent / 'index.html'
            else:
                yield file_source, file_destination / 'index.html'


def render_documents(source: Path, destination: Path, template: Path = None):
    """Load all documents from within the source directory
    and its subdirectories and render them onto a template file.
    Save all renders in the destination directory.
    """

    # Load template
    if template is not None:
        with open(template, 'r') as f:
            template = f.read()

    # Iterate over the source and destination directories for each document
    for fsource, fdestination in find_documents(source, destination):
        # Load document
        with open(fsource, 'r') as f:
            document = f.read()

        # Prepare document and render it
        metadata, document = extract_metadata(document)
        rendered = marquedown(document)

        # Ensure destination directory
        os.makedirs(fdestination.parent, exist_ok=True)

        with open(fdestination, 'w') as f:
            # Format to template if provided
            if template is not None:
                rendered = template.format_map(defaultdict(str, **metadata, document=rendered))
            # Write to destination
            f.write(rendered)
            print(f'Rendered document: {fsource.relative_to(source)}')