# Plugins

Drop any `.py` file here that contains a list named `MODULES`.

Example:

```python
def hello():
    print("plugin works")

MODULES = [
    ("Hello Plugin", "example plugin", hello),
]
```

They will appear automatically in the PLUGINS category.
