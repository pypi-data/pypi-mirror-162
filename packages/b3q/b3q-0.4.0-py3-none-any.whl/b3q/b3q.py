"""
Boto3 utility library that supports parameter-driven and predicate-driven
retrieval of collections of AWS resources.
"""
from __future__ import annotations
from typing import Optional, Callable, Iterable
import doctest

def get(
        method: Callable,
        arguments: Optional[dict] = None,
        constraints: Optional[dict] = None,
        attribute: Optional[str] = None
    ) -> Iterable:
    # pylint: disable=line-too-long # Accommodate long URL.
    """
    Assemble all items in a paged response pattern from the supplied AWS API retrieval method.

    .. |get_function| replace:: ``Lambda.Client.get_function``
    .. _get_function: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.get_function

    :param method: AWS API retrieval method (such as |get_function|_).
    :param arguments: Named arguments to be supplied to the method.
    :param constraints: Attribute-value pairs that must appear in an item (or it is excluded).
    :param attribute: Attribute (of a response object) under which retrieved items are found.

    >>> import itertools
    >>> def method(identifier, position=None):
    ...     if position is None:
    ...         position = 0
    ...     return dict({
    ...         'items': [{'value': position, 'parity': position % 2}],
    ...     }, **({'position': position + 1} if position <= 4 else {}))
    >>> [item['value'] for item in itertools.islice(get(
    ...     method,
    ...     arguments={'identifier': 0},
    ...     constraints={'parity': 0}
    ... ), 0, 4)]
    [0, 2, 4]
    """
    arguments = {} if arguments is None else arguments
    constraints = {} if constraints is None else constraints
    attribute = 'items' if attribute is None else attribute
    position = {}
    while True:
        response = method(**arguments, **position)
        for item in response.get(attribute, []):
            if all(item[k] == v for (k, v) in constraints.items()):
                yield item
        if not 'position' in response:
            break
        position = {'position': response['position']}

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
