try:
    from . import _version

    __version__ = _version.__version__
except ImportError:
    pass

__all__ = [
	'gravity_density',
]