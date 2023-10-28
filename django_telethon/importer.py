import importlib


def import_attribute(path):
    package, attr = path.rsplit(".", 1)
    attribute = getattr(importlib.import_module(package), attr)
    return attribute
