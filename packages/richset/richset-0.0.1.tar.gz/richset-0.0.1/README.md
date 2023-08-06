# richset

```python
from dataclasses import dataclass
from richset import RichSet


@dataclass(frozen=True)
class Something:
    id: int
    name: str


richset = RichSet.from_list([
    Something(1, 'one'),
    Something(2, 'two'),
])
richset.to_list()  # => [Something(1, 'one'), Something(2, 'one')]
richset.to_dict(lambda s: s.id)  # => {1: Something(1, 'one'), 2: Something(2, 'one')}
```


# LICENSE

The 3-Clause BSD License. See also LICENSE file.
