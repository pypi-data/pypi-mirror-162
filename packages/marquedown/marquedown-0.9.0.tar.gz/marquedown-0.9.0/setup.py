# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['marquedown', 'marquedown.commands']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.3.6,<4.0.0', 'PyYAML>=6.0,<7.0']

setup_kwargs = {
    'name': 'marquedown',
    'version': '0.9.0',
    'description': 'Extending Markdown further by adding a few more useful notations.',
    'long_description': '# Marquedown\n\nExtending Markdown further by adding a few more useful notations.\nIt can be used in place of `markdown` as it also uses and applies it.\n\n## Examples\n\n### Blockquote with citation\n\nThis is currently limited to the top scope with no indentation.\nSurrounding dotted lines are optional.\n\n#### Example\n\n##### Marquedown\n\n```md\n......................................................\n> You have enemies? Good. That means you\'ve stood up\n> for something, sometime in your life.\n-- Winston Churchill\n\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\n```\n\n##### HTML\n\n```html\n<blockquote>\n    <p>\n        You have enemies? Good. That means you\'ve stood up\n        for something, sometime in your life.\n    </p>\n    <cite>Winston Churchill</cite>\n</blockquote>\n```\n\n### Embed video\n\n#### YouTube\n\n##### Marquedown\n\n```md\n![dimweb](https://youtu.be/VmAEkV5AYSQ "An embedded YouTube video")\n```\n\n##### HTML\n\n```html\n<iframe\n    src="https://www.youtube.com/embed/VmAEkV5AYSQ"\n    title="An embedded YouTube video" frameborder="0"\n    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"\n    allowfullscreen>\n</iframe>\n```\n\n### BBCode HTML tags\n\nThese tags allow you to put Marquedown inside HTML tags. This is done by finding and replacing them with their represented HTML after all other Marquedown has been rendered.\n\n#### Tags and classes\n\nThe naming scheme is the same as in CSS, e.g. `tag.class1.class2`\nIf `tag` is omitted, it is treated to be `div`\n\n#### ID:s\n\nID:s are supported using `#beans` at the end of the tag, ex. `[p#beans]`\n\n#### Example\n\n##### Marquedown\n\n```md\n[section]\n[.bingo]\nA regular **paragraph** written in Marquedown, but *within* other HTML tags.\n[//]\n\n[tag.class1.class2] [/tag]\n```\n\n##### HTML\n\n```html\n<section>\n<div class="bingo">\n    <p>\n        A regular <strong>paragraph</strong> written in Marquedown, but <em>within</em> other HTML tags.\n    </p>\n</div></section>\n\n<tag class="class1 class2"> </tag>\n```\n\n### Label list\n\n#### Example\n\n##### Marquedown\n\n```md\n(| email: [jon@webby.net](mailto:jon@webby.net)\n(| matrix: [@jon:webby.net](https://matrix.to/#/@jon:webby.net)\n(| runescape: jonathan_superstar1777\n```\n\n##### HTML\n\n```html\n<ul class="labels">\n    <li class="label label-email">\n        <a href="mailto:jon@webby.net">\n            jon@webby.net\n        </a>\n    </li>\n    <li class="label label-matrix">\n        <a href="https://matrix.to/#/@jon:webby.net">\n            @jon:webby.net\n        </a>\n    </li>\n    <li class="label label-runescape">\n        jonathan_superstar1777\n    </li>\n</ul>\n```\n\n### QR codes\n\nQR codes can be generated and referenced automatically via the `render` command. If you want to generate QR codes with `marquedown.marquedown`, you can follow the example below.\n\n#### Example\n\n##### Marquedown\n\n```md\n![qr:monero-wallet](monero:abcdefghijklmnopqrstuvwxyz)\n```\n\n##### Python\n\n```py\nfrom marquedown import marquedown\n\nwith open(\'document.mqd\', \'r\') as f:\n    document = f.read()\n\nwith open(\'public/document.html\', \'w\') as f:\n    rendered = marquedown(document, qrgen=\'public/qr:qr\')\n    f.write(rendered)\n```\n\nThe string provided to `qrgen` is two paths separated by a colon.\n\n1. Where to save the generated images\n2. What directory to reference in the HTML `src` parameter\n\n##### The generated HTML\n\n```html\n<img src="qr/qr-0-monero-wallet.png" alt="monero-wallet">\n```\n\n## Commands\n\n### `render`: Render documents\n\nYou can render an entire directory and its subdirectories of Markdown or Marquedown documents. This can be used to automate rendering pages for your website.\n\nDo `python -m marquedown render --help` for list of options.\n\n#### Example\n\nFor a few of my websites hosted on GitLab, I have it set up to run *this* on push:\n\n```sh\n# Render document\npython -m marquedown render -i "./mqd" -o "./public" -t "./templates/page.html"\n\n# This is for the GitLab Pages publication\nmkdir .public\ncp -r public .public\nmv .public public  \n```',
    'author': 'Maximillian Strand',
    'author_email': 'maximillian.strand@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/deepadmax/marquedown',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
