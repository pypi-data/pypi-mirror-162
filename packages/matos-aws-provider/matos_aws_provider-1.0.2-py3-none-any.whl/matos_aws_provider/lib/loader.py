import importlib
from importlib import resources


class ModuleInterface:
    """Represents a plugin interface. A plugin has a single register function."""

    @staticmethod
    def register() -> None:
        """Register the necessary items in the game character factory."""


def import_module(name: str) -> ModuleInterface:
    """Imports a module given a name."""
    return importlib.import_module(name)  # type: ignore


def load_plugins(package: str) -> None:
    """Loads the plugins defined in the plugins list."""
    files = resources.contents(package)
    plugins = [f[:-3] for f in files if f.endswith(".py") and f[0] != "_"]

    for plugin_file in plugins:
        plugin = import_module(f"{package}.{plugin_file}")
        plugin.register()
