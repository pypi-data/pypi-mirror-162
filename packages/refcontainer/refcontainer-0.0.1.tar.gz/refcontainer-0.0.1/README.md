# Reference Container

This library implements a simple container which holds a single value.
The container is completely typed, supports an optional default value,
supports readonly mode, and does runtime type checking.

Examples:

```python
from refcontainer import Ref, ReadOnlyError

# Initialize with value
str_ref = Ref('hello')
assert str_ref.current == 'hello'
str_ref.clear()
_ = str_ref.current  # raises AttributeError

str_ref.current = 'world'
assert str_ref.current == 'world'
str_ref.current = 0  # raises TypeError

str_ref.engrave('hello')
str_ref.current = 'world'  # raises ReadOnlyError

# Initialize as readonly (engraved)
str_ref = Ref.readonly('hello')
str_ref.clear()  # raises ReadOnlyError
assert str_ref.current == 'hello'

# Initialize with type tags
ref = Ref[str | int]('hello')
assert ref.current == 'hello'
ref.current = 'world'
ref.current = 0
with raises(TypeError):
    ref.current = 0.

# Disable type checking
ref = Ref[Any]('hello')

# Initialize with type but without value
num_ref = Ref[float]()
with raises(AttributeError):
    _ = num_ref.current
num_ref.current = 0.
assert num_ref.current == 0
num_ref.current = 'hello'  # raises TypeError
```
