"""Asserts the shapes according to the spec.

The spec notation is inspired Einstein notation. We show some examples below to illustrate.

- "mnk,mnk" asserts that the two input shapes, each having 3 dimensions, are exactly the same.
  "m", "n", "k" are all identifiers.
- "_nk,_nk" asserts that the two input shapes are only the same along the second and thrid
  dimensions, while the first dimensions are not checked. "_" is used as a wildcard.
- "mnk,mnk..." asserts that the input shapes have the same "shape" for the first three
  dimensions, and the remaining dimensions of the second shape is not checked.
"""

from .assertshape import (
    assert_shape,
    assertShape,
    assertshape,
    test_shape,
    testShape,
    testshape,
)
