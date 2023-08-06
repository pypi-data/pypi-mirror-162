"""Tests"""

import unittest
from .assertshape import _assert_shape


class TestAssertShapeLib(unittest.TestCase):
    """Unit tests."""

    true_cases = [
        ("_", [(1,)]),
        ("_", [(2,)]),
        ("n", [(1,)]),
        ("n", [(2,)]),
        ("mn", [(1, 1)]),
        ("mn", [(1, 2)]),
        ("_n", [(1, 1)]),
        ("_n", [(1, 2)]),
        ("nn", [(1, 1)]),
        ("n,n", [(1,), (1,)]),
        ("n,m", [(1,), (1,)]),
        ("n,m", [(1,), (2,)]),
        ("_,m", [(1,), (1,)]),
        ("_,m", [(1,), (2,)]),
        ("_, m", [(1,), (2,)]),
        ("_m,m", [(2, 1), (1,)]),
        ("n,...", [(1,), (1,)]),
        ("n,...", [(1,), (2,)]),
        ("n,...", [(1,), (1, 2, 3)]),
        ("n,...", [(1,), (2, 2, 3)]),
        ("n,n...", [(1,), (1, 2, 2, 3)]),
        ("n,...n", [(1,), (2, 2, 3, 1)]),
        ("n...,...n", [(1, 9, 3), (2, 2, 3, 1)]),
        ("...n,...n", [(9, 3, 1), (2, 2, 3, 1)]),
        ("_,...", [(1,), (1,)]),
        ("_,...", [(1,), (2, 3, 4)]),
        ("mnk,mnl...,nkl...", ((1, 2, 3), (1, 2, 4, 5), (2, 3, 4, 6, 6))),
        ("mnk,mnl...,nkl...", ((1, 2, 3), (1, 2, 4, 5), (2, 3, 4, 6, 6))),
    ]

    false_cases = [
        ("n,n", ((1,), (2,))),
        ("nn", ((1, 2),)),
        ("mnk,mnl...,nkl...", ((1, 2, 3), (1, 2, 4, 5), (1, 3, 4, 6, 6))),
    ]

    def test_true_cases(self):
        """Basic true cases."""
        for spec, inputs in self.true_cases:
            with self.subTest(spec):
                result, msg = _assert_shape(spec, inputs)
                assert result, msg

    def test_false_cases(self):
        """Basic true cases."""
        for spec, inputs in self.false_cases:
            with self.subTest(spec):
                result, _ = _assert_shape(spec, inputs)
                assert not result


if __name__ == "__main__":
    unittest.main()
