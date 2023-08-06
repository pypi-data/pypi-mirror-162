# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modupipe']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'modupipe',
    'version': '1.0.0',
    'description': 'A modular and extensible ETL-like pipeline builder',
    'long_description': '[![Build](https://github.com/vigenere23/modupipe/actions/workflows/build.yml/badge.svg)](https://github.com/vigenere23/modupipe/actions/workflows/build.yml)\n\n# ModuPipe : A modular and extensible ETL-like pipeline builder\n\n## Benefits\n\n- Entirely typed\n- Abstract, so it fits any use case\n- Class-based for easy configurations and injections\n\n## Usage\n\nExtract-Transform-Load (ETL) pipelines are a classic form of data-processing pipelines used in the industry. It consists of 3 main elements:\n\n1. An **`Extractor`**, which returns data in a stream-like structure (`Iterator` in Python) using a pull strategy.\n2. Some **`Mapper`** (optional), which transforms (parse, converts, filters, etc.) the data obtained from the source(s). Mappers can be chained together and chained to an extractor (with `+`) in order to form a new extractor.\n3. A **`Loader`**, which receives the maybe-transformed data using a push strategy. Loaders can be multiple (with `LoaderList`) or chained together (with `+`).\n\nTherefore, those 3 processes are offered as interfaces, easily chainable and interchangeable at any time.\n\nAn interface `Runnable` is also offered in order to interface the concept of "running a pipeline". This enables a powerfull composition pattern for wrapping the execution behaviour of runnables.\n\n## Examples\n\nUsage examples are present in the [examples](./examples) folder.\n\n## Discussion\n\n### Optimizing pushing to multiple loaders\n\nIf you have multiple loaders (using the `LoaderList` class or many chained `PushTo` mappers), but performance is a must, then you should use a multi-processing approach (with `modupipe.runnable.MultiProcess`), and push to 1 queue per loader. Each queue will also become a direct extractor for each loader, all running in parallel. This is especially usefull when at least one of the loaders takes a long processing time.\n\nAs an example, let\'s take a `Loader 1` which is very slow, and a `Loader 2` which is normally fast. You\'ll be going from :\n\n```\n┌────── single pipeline ──────┐        ┌──────────────── single pipeline ───────────────┐\n Extractor ┬─⏵ Loader 1 (slow)    OR    Extractor ──⏵ Loader 1 (slow) ──⏵ Loader 2 (late)\n           └─⏵ Loader 2 (late)\n```\n\nto :\n\n```\n┌────── pipeline 1 ──────┐               ┌────────── pipeline 2 ─────────┐\n Extractor ┬─⏵ PutToQueue ──⏵ Queue 1 ⏴── GetFromQueue ──⏵ Loader 1 (slow)\n           └─⏵ PutToQueue ──⏵ Queue 2 ⏴── GetFromQueue ──⏵ Loader 2 (not late)\n                                         └──────────── pipeline 3 ───────────┘\n```\n\nThis will of course not accelerate the `Loader 1` processing time, but all the other loaders performances will be greatly improved by not waiting for each other.\n',
    'author': 'vigenere23',
    'author_email': 'lolgab1@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vigenere23/modupipe',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
