from setuptools import setup

name = "types-flake8-2020"
description = "Typing stubs for flake8-2020"
long_description = '''
## Typing stubs for flake8-2020

This is a PEP 561 type stub package for the `flake8-2020` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `flake8-2020`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/flake8-2020. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `959840a12dde2896100250df58590994e2cdc2e9`.
'''.lstrip()

setup(name=name,
      version="1.7.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/flake8-2020.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['flake8_2020-stubs'],
      package_data={'flake8_2020-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
