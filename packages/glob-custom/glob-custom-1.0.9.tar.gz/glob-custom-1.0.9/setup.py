import os
from setuptools import setup


"""
:authors: DarkRastafar
:license: Apache License
:copyright: (c) 2022 DarkRastafar
"""


long_description = '''smth'''


version = "1.0.9"


if os.path.exists('C:\\CustomMethods\\config.py'):
    setup(
        name="glob-custom",
        version=version,
        author="Example Author",
        author_email="author@example.com",
        url="https://github.com/pypa/sampleproject",
        description=("A small example package"),
        long_description=long_description,
        long_description_content_type='text/markdown',
        license="LICENSE",
        classifiers=[
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
            ],
        install_requires=['loguru>=0.6.0', 'requests']
    )
else:
    pass
