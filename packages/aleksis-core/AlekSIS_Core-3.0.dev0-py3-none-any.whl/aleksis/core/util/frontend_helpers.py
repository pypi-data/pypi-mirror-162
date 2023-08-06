import os

from .core_helpers import get_app_module, get_app_packages


def get_apps_with_assets():
    """Get a dictionary of apps that ship frontend assets."""
    assets = {}
    for app in get_app_packages():
        mod = get_app_module(app, "apps")
        path = os.path.join(os.path.dirname(mod.__file__), "assets")
        if os.path.isdir(path):
            package = ".".join(app.split(".")[:-2])
            assets[package] = path
    return assets
