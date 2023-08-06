#!/usr/bin/env python3
import pathlib

import setuptools
from ruth_tts_transformer import VERSION

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

core_requirements = [
    'tqdm',
    'rotary_embedding_torch',
    'inflect',
    'progressbar',
    'einops',
    'unidecode',
    'scipy',
    'librosa',
    'transformers',
    'tokenizers',
]

setuptools.setup(
    name='ruth-text-to-speech',
    description="A Python CLI for Ruth NLP",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="",
    author='Puretalk',
    author_email='info@puretalk.ai',
    version=VERSION,
    install_requires=core_requirements,
    python_requires='>=3.7,<3.9',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={"console_scripts": ["ruth = ruth.cli.cli:entrypoint"]},
)
