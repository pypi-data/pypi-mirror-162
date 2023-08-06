# ptorru-matmul

Learning about pipy, distributing a simple matrix multiply example

To consult how to distribute a package in PyPI take a look at the [publish_notes.md](https://github.com/ptorru/ptorru-matmul/blob/main/publish_notes.md)

# Installing this package

Using [PyPI](https://pypi.org)

```bash
pip install ptorru-matmul
```

Alternatively use [poetry](https://python-poetry.org)

```bash
poetry add ptorru-matmul
```

# Using this package

```python
import numpy as np
from ptorru_matmul import matmul
sides = 3
a = np.arange(sides*sides).reshape(sides,sides)
b = np.arange(sides*sides).reshape(sides,sides)
c = matmul(a,b)
assert np.array_equal(c, np.matmul(a,b))
print(a,b)
print(c)
```
