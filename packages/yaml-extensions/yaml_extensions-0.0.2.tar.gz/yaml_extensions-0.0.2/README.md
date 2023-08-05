# Extensions for PyYAML

## Inclusions

This implements a simple inclusion interface. If used, any inclusions will be
assumed to be relative paths to the YAML file being loaded, if the location can
be determined, otherwise relative to the current working directory.

```python
from yaml_extensions.inclusions import InclusionSafeLoader

with open("outer.yaml", "r") as yaml_fp:
    my_yaml = yaml.load(
        yaml_fp,
        loader=InclusionSafeLoader
    )
```

This allows `outer.yaml` to be split into two files, e.g.:

__outer.yaml__
```yaml
fizz:
    buzz: !include "inner.yaml"
```

__inner.yaml__
```yaml
bar:
    bell: 51
```

will become:

```python
{
    "fizz": {
        "buzz": {
            "bar": {
                "bell": 51
            }
        }
    }
}
```
