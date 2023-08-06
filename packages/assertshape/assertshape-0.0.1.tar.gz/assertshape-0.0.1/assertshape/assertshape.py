"""Asserts the shapes according to the spec."""


def _substitute(spec, table):
    """Substitute free variables in the spec string using the table as the environment."""
    spec = spec.replace("...", "*")
    return tuple(
        map(
            lambda id: table.get(id, id) if id != "*" else "...",
            spec,
        )
    )


def _assert_shape(spec, shapes):
    """Implementation of assert_shape."""
    specs = spec.split(",")
    assert len(specs) == len(
        shapes
    ), f"The spec expects {len(specs)} inputs but we only got {len(shapes)}"

    table = dict()
    for rawspec, shape in zip(specs, shapes):
        spec = rawspec.replace("...", "*").replace(" ", "")
        assert (
            spec.count("*") <= 1
        ), f"Spec can only have at most one ellipsis, got '{rawspec}"

        match_tail = False
        for rank, ident in enumerate(spec):
            # wildcard
            if ident == "_":
                continue

            # ellipsis
            if ident == "*":
                assert (
                    rank == 0 or rank == len(spec) - 1
                ), f"The ellipsis can only occur in the beginning or the end of the spec, got '{rawspec}'"

                # at the end
                if rank == len(spec) - 1:
                    break

                # at the beginning
                match_tail = True

            if match_tail:
                rank = -1 * (len(spec) - rank)

            # normal identifier
            assert len(spec.replace("*", "")) <= len(
                spec
            ), f"The spec string '{rawspec}' has higher rank than the shape {shape}"

            # id not defined yet
            expected = table.get(ident)
            if expected is None:
                table[ident] = shape[rank]

            # id already defined
            else:
                # but has a different value
                if shape[rank] != expected:
                    return (
                        False,
                        f"Expecting {shape} with spec '{rawspec}' to "
                        f"match {_substitute(rawspec, table)}",
                    )

    return True, ""


def _adapt_to_tuples(shapes):
    """Adapts the shapes to a list of tuples."""
    shapes = list(shapes)
    if len(shapes) > 0:
        # base case
        if isinstance(shapes[0], tuple):
            pass
        # has .shape
        elif "shape" in dir(shapes[0]) and isinstance(shapes[0].shape, tuple):
            shapes = map(lambda s: s.shape, shapes)
        # not implemented
        else:
            raise NotImplementedError(
                f"The input type {type(shapes[0])} is not directly supported. "
                "Please map them to a list of tuples."
            )
    return shapes


def assert_shape(spec, shapes, msg=None):
    """Assert the shapes of the inputs based on the spec."""
    shapes = _adapt_to_tuples(shapes)
    result, err = _assert_shape(spec, shapes)
    if msg:
        assert result, f"{err}: {msg}"
    else:
        assert result, err


def test_shape(spec, shapes):
    "Test the shapes. Same functionality, just returns test results without assertions."
    shapes = _adapt_to_tuples(shapes)
    return _assert_shape(spec, shapes)


assertShape = assert_shape
assertshape = assert_shape
testShape = test_shape
testshape = test_shape
