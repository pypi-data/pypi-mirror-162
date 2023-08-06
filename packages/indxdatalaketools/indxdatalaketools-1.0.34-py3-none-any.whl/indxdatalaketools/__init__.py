from importlib.metadata import version, PackageNotFoundError
# pre-3.8 import statement
# from importlib_metadata import version, PackageNotFoundError
VERSION_FALLBACK = "0.0.1"
__version__ = ''
try:
    __version__ = version('indxdatalaketools')
except PackageNotFoundError:
    # package is not installed
    # assign signal or sane value as a default
    __version__ = VERSION_FALLBACK
    pass