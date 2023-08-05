# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['animal_language']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'animal-language',
    'version': '0.1.1',
    'description': 'Customize a word set, and then use the words in this set to represent any sentence.',
    'long_description': '# Animal Language\n\nCustomize a word set, and then use the words in this set to represent any sentence.\n\n## Install\n\n```\npip install --upgrade animal-language\n```\n\n## Usage\n\nTo encode a sentence with these characters and words:\n\n`m, oo, b, aa, z`\n\n(or use moo, baa, zzz, but it will increase the encoded string\'s length)\n\n\n### 1) Create a Translater\n\n```python\nfrom animal_language import ALTranslater\n\ntranslater = ALTranslater([\'m\', \'oo\', \'b\', \'aa\', \'z\'])\n```\n\n### 2) Encode Any String\n\nuse the translater to encode any string you want.\n\n```python\nencoded_str = translater.encode(\'hello, this is a test\')\n```\n\nThe encoded_str will be like :\n\n`oooombbooboozmmbaabbmooaaoobaambzzooaaaaaazmbmbooaam`\n\n### 3) Decode the Encoded String\n\nAlso use the translater to decode the encoded_str.\n\n```python\ndecoded_str = translater.decode(encoded_str)\n```\n\nThe decoded_str is equal to the string you encoded\n\n\n## Other Information\n\n+ The word list must be like "prefix codes", lists like `[\'a\', \'ab\']` will not supported.\n+ You can set the encoding of the input string.\n+ JUST HAVE FUN AND ENJOY THIS bmoooombaaooooaambooz !',
    'author': 'chnzzh',
    'author_email': 'chnzzh@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chnzzh/animal-language',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
