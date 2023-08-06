# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hash_chunker']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hash-chunker',
    'version': '0.1.7',
    'description': 'Generator that yields hash chunks for distributed data processing.',
    'long_description': '# Python Hash Chunker\n\nGenerator that yields hash chunks for distributed data processing.\n\n### TLDR\n\n```\n# pip install hash-chunker\nfrom hash_chunker import HashChunker\n\nchunks = list(HashChunker().get_chunks(chunk_size=1000, all_items_count=2000))\nassert chunks == [("", "8000000000"), ("8000000000", "ffffffffff")]\n\n# or\nhash_chunker = HashChunker(chunk_hash_length=3)\nchunks = list(hash_chunker.get_chunks(500, 1500))\nassert chunks == [(\'\', \'555\'), (\'555\', \'aaa\'), (\'aaa\', \'fff\')]\n\n# use chunks as tasks for multiprocessing\nquery_part = "hash > :from_hash AND hash <= :to_hash"\nparams = {"from_hash": chunk[0], "to_hash": chunk[1]}\n```\n\n## Description\n\nImagine a situation when you need to process huge amount data rows in parallel.\nEach data row has a hash field and the task is to use it for chunking.\n\nPossible reasons for using hash field and not int id field:\n- No auto increment id field.\n- Field id has many blank lines (1,2,3, 100500, 100501, 1000000).\n- Chunking by id will break data that must be in one chunk to different chunks\n(in user behavioral analytics id can be autoincrement for all users actions and\nuser_session hash is linked to concrete user, so if we chunk by id one user session may\nnot be in one chunk).\n\n## Installation\n\nRecommend way to install Hash Chunker is pip.\n\n```\npip install hash-chunker\n```\n\n## Usage\n\nImport Hash Chunker.\n```\nfrom hash_chunker import HashChunker\n```\n\nCreate class instance.\n```\nhash_chunker = HashChunker()\n\n# or use chunk_hash_length key word arguments to limit generated hashes length\nhash_chunker = HashChunker(chunk_hash_length=3)\n```\n\nGet chunks by providing chunk_size and all_items_count.\n\n```\nchunks = list(hash_chunker.get_chunks(chunk_size=500, all_items_count=1500))\n\n# or skip positional arguments names\nchunks = list(hash_chunker.get_chunks(500, 1500))\n\n# or use yielded chunks in loop\nfor chunk in hash_chunker.get_chunks(500, 1500):\n    print(chunk)\n```\n\n## Support\nYou may report bugs, ask for help, and discuss various other issues\non the [bug tracker](https://github.com/whysage/hash_chunker/issues).\n',
    'author': 'Volodymyr Kochetkov',
    'author_email': 'whysages@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/whysage/hash_chunker',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
