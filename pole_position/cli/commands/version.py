from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("poleposition")
except PackageNotFoundError:
    __version__ = "0.0.7"