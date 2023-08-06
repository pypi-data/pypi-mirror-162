# assertshape

![Unit Test Status](https://github.com/steinwaywhw/assertshape/actions/workflows/unit-tests.yml/badge.svg)
![![PyPI](https://img.shields.io/pypi/v/requests?logo=pypi)](https://pypi.org/project/assertshape/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/assertshape?logo=python)

Python library for asserting n-dim array shapes using Einstein notations.

Examples: 

```python
from assertshape import assertshape

assertshape("nmk,mkn", [(1,2,3), (2,3,1)])
assertshape("nmk,m_n", [(1,2,3), (2,42,1)])
assertshape("nmk,mkn...", [(1,2,3), (2,3,1,4,5,6)])
```
