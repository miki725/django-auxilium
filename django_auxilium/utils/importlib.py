"""
Collection of utilities which help in importing things in Python
"""

from django.utils import importlib


def dynamic_import(to_import):
    """
    Method which dynamically imports either a module or an attribute
    of the module.

    Parameters
    ----------
    to_import : str
        Python path (dot-separated) of the module or it's attribute to import.
    """
    try:
        imported = importlib.import_module(to_import)

    except ImportError:
        split_to_import = to_import.split('.')
        module, attr = '.'.join(split_to_import[:-1]), split_to_import[-1]
        module = importlib.import_module(module)
        imported = getattr(module, attr)

    return imported
