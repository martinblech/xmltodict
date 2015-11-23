"""xmltodict"""
__license__ = 'MIT'
__version__ = '0.9.3'

__author__ = 'Martin Blech'
__email__ = 'martinblech@gmail.com'
__url__ = 'https://github.com/martinblech/xmltodict'

from .xmltodict import parse
from .xmltodict import unparse

__all__ = [
    parse.__name__,
    unparse.__name__,
]


if __name__ == '__main__':  # pragma: no cover
    import sys
    import marshal

    (item_depth,) = sys.argv[1:]
    item_depth = int(item_depth)

    def handle_item(path, item):
        marshal.dump((path, item), sys.stdout)
        return True

    try:
        root = parse(sys.stdin,
                     item_depth=item_depth,
                     item_callback=handle_item,
                     dict_constructor=dict)
        if item_depth == 0:
            handle_item([], root)
    except KeyboardInterrupt:
        pass
