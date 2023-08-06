## Calendric-lib
[![Downloads](https://pepy.tech/badge/calendric-lib)](https://pepy.tech/project/calendric-lib)
![PyPI - Status](https://img.shields.io/pypi/status/calendric-lib)
[![GitHub issues](https://img.shields.io/github/issues/saadbinmunir/Calendric-lib)](https://github.com/saadbinmunir/Calendric-lib/issues)
[![GitHub stars](https://img.shields.io/github/stars/saadbinmunir/Calendric-lib)](https://github.com/saadbinmunir/Calendric-lib/stargazers)
[![GitHub license](https://img.shields.io/github/license/saadbinmunir/Calendric-lib)](https://github.com/saadbinmunir/Calendric-lib/blob/main/LICENSE)

##  About
Calendric-lib is a creative package for calendrical conversion operations in Python.

## Requirements

Calendric-lib requires python 3.6 or greater.

## Installation

Install with pip:

```
pip install calendric-lib
```

If you are using the old version of calendric-lib and want to update it:

```
pip install --upgrade calendric-lib
```

## Examples

```python
import calendric_lib as cl

cl.MonthToNum('January')
# Output: 1

cl.AbbrMonthToNum('Jan')
# Output: 1

cl.NumToAbbrMonth(5)
# Output: May

cl.NumToMonth(7)
# Output: July
```