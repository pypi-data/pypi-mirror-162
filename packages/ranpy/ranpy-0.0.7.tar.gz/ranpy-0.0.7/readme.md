To update the package update pyproject.toml with a new version number and then run:

```python
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine
python3 -m build
twine upload dist/*
```

![Copy to clipboard](https://packaging.python.org/en/latest/_static/copy-button.svg)

