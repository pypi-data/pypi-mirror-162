import argparse
from pathlib import Path


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command', required=True)

# `render`: Render Marquedown documents

render = subparsers.add_parser('render', help='Render Markdown and Marquedown documents')
render.add_argument('-i', '--source',
    dest='source',
    help='Source root directory of Marquedown documents',
    type=Path,
    required=True,
)
render.add_argument('-o', '--destination',
    dest='destination',
    help='Destination root directory for rendered and templated documents',
    type=Path,
    required=True,
)
render.add_argument('-t', '--template',
    dest='template',
    help='Template HTML file. Must contain `{document}` where to insert the rendered document.',
    type=Path,
    default=None,
)




if __name__ == '__main__':
    args = parser.parse_args()
    
    # `render`: Render Marquedown documents
    if args.command == 'render':
        from .commands.render import render_documents
        render_documents(args.source, args.destination, args.template)