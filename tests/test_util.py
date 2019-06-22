from pretf.util import once


def test_once():

    result = []

    @once
    def append_one():
        append_one()  # recursive calls do nothing
        result.append(1)
        return True

    @once
    def append_two():
        result.append(2)
        return True

    # The first call is normal, it returns True
    assert append_one() is True
    assert result == [1]

    # Subsequent calls do nothing and return nothing.
    assert append_one() is None
    assert append_one() is None
    assert result == [1]

    # Test that multiple functions can use the decorator.
    assert append_two() is True
    assert result == [1, 2]
    assert append_two() is None
    assert append_two() is None
    assert result == [1, 2]


def test_once_methods():
    class Append:
        def __init__(self):
            self.result = []

        @once
        def append(self, value):
            self.append(value)  # recursive calls do nothing
            self.result.append(value)
            return True

    a = Append()
    b = Append()

    assert a.append(1) is True
    assert a.append(1) is None
    assert a.append(1) is None
    assert a.result == [1]

    assert a.append(2) is True
    assert a.append(2) is None
    assert a.append(2) is None

    assert a.result == [1, 2]

    assert b.append(3) is True
    assert b.append(3) is None
    assert b.append(3) is None

    assert b.result == [3]
