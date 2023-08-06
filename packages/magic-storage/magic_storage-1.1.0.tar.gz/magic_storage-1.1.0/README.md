<h2 align="center">Magic Storage cooler than you think!</h2>

---

<p align="center">
    <a href="https://pypi.org/project/magic-storage/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/magic_storage"></a>
    <a href="https://pycqa.github.io/isort/"><img alt="isort" src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336"></a>
    <a href="https://github.com/Argmaster/magic-storage/actions"><img alt="Test Status" src="https://github.com/Argmaster/magic-storage/workflows/Test%20suite%20CI%20run/badge.svg"></a>
    <a href="https://github.com/Argmaster/magic-storage/actions"><img alt="Docs Status" src="https://github.com/Argmaster/magic-storage/workflows/Deploy%20documentation/badge.svg"></a>
    <a href="https://github.com/Argmaster/magic-storage/actions"><img alt="Docs Status" src="https://github.com/Argmaster/magic-storage/workflows/Deploy%20documentation/badge.svg"></a>
    <a href="https://pypi.org/project/magic-storage/"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/magic-storage"></a>
    <a href="https://github.com/Argmaster/magic-storage/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/Argmaster/magic-storage"></a>
    <a href="https://github.com/Argmaster/magic-storage/pulls"><img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/Argmaster/magic-storage"></a>
    <a href="https://github.com/Argmaster/magic-storage/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/Argmaster/magic-storage"></a>
    <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/v/tag/Argmaster/magic-storage?label=version">
</p>

Magic storage is a Python library that provides tools to easily write, read and
delete resources for testing. This applies, of course, to resources that are
difficult to obtain but not very expensive to store locally and, in addition,
do not change. A good example are responses from REST APIs or at least those of
them that are not live data.

The library consists of a set of classes that implement storage using the file
system and temporary storage in RAM. All tools can be accessed through the
MagicStorage class.

## Installing

Install and update using pip:

```
$ pip install -U magic_storage
```

## Example

```python
from typing import Any
from magic_storage import MagicStorage


def very_expensive_get() -> Any:
    ...


response = (
    MagicStorage()
    .filesystem(__file__)
    .cache_if_missing("Nice thing", lambda: very_expensive_get())
)

```

## Documentation

Online documentation is available on
[Github pages](https://argmaster.github.io/magic-storage/).
