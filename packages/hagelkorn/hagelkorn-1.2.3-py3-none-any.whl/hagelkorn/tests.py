import datetime
import timeit
import unittest

from . import core


class TestHagelkorn(unittest.TestCase):
    def test_key_length(self):

        D, K, T = core.key_length(
            overflow_years=1, resolution=core.Resolution.days, B=10
        )
        assert D == 3
        assert K == 10 ** D
        assert T < core.Resolution.days

        D, K, T = core.key_length(
            overflow_years=30, resolution=core.Resolution.days, B=27
        )
        assert K == 27 ** D
        assert T < core.Resolution.days

        pass

    def test_base(self):
        assert core.base(9, "0123456789ABCDEF", 2) == "09"
        assert core.base(13, "0123456789ABCDEF", 2) == "0D"
        assert core.base(16, "0123456789ABCDEF", 2) == "10"
        assert core.base(256, "0123456789ABCDEF", 2) == "100"
        pass

    def test_monotonic(self):
        id = core.monotonic(
            resolution=core.Resolution.days,
            now=datetime.datetime(2018, 12, 31, 23, 59, 59),
            alphabet="0123456789",
            start=datetime.datetime(2018, 1, 1),
            overflow_years=1,
        )
        assert id == "999"

        pass

    def test_equivalence(self):
        hs = core.HagelSource()
        now = datetime.datetime.now()

        assert hs.monotonic(now) == core.monotonic(now=now)

        pass

    def test_random(self):
        ids = [core.random() for i in range(100)]
        assert len(set(ids)) == 100
        pass


class TestHagelSource(unittest.TestCase):
    def test_init(self):
        hs = core.HagelSource(overflow_years=42)
        assert (hs.end - hs.start).total_seconds() == hs.total_seconds
        assert hs.total_seconds == 42 * 31536000
        assert hs.B == len(hs.alphabet)
        assert hs.B ** hs.digits == hs.combinations
        assert hs.total_seconds / hs.combinations == hs.resolution
        pass

    def test_monotonic(self):
        hs = core.HagelSource(
            resolution=core.Resolution.days,
            alphabet="0123456789",
            start=datetime.datetime(2018, 1, 1),
            overflow_years=1,
        )
        id = hs.monotonic(now=datetime.datetime(2018, 12, 31, 23, 59, 59))

        assert len(id) == hs.digits
        assert id == "999"
        pass

    def test_t_0(self):
        hs = core.HagelSource()
        first = hs.monotonic(now=hs.start)
        assert set(first) == set(hs.alphabet[0]), (
            "ID at start time was expected to be all {} but"
            " the monotonicd ID was {}".format(hs.alphabet[0], first)
        )
        pass

    def test_t_overflow(self):
        hs = core.HagelSource()
        overflow = hs.monotonic(now=hs.end)

        assert len(overflow) == hs.digits + 1
        assert overflow == hs.alphabet[1] + hs.alphabet[0] * hs.digits

        pass


if __name__ == "__main__":
    hs = core.HagelSource()
    p_obj = min(timeit.Timer(hs.monotonic).repeat(number=100000)) / 100000
    p_fn = min(timeit.Timer(core.monotonic).repeat(number=100000)) / 100000
    p_rnd = min(timeit.Timer(core.random).repeat(number=100000)) / 100000
    print("hs.monotonic() takes {} µs per call".format(p_obj * 1000 * 1000))
    print("monotonic() takes {} µs per call".format(p_fn * 1000 * 1000))
    print("random() takes {} µs per call".format(p_rnd * 1000 * 1000))
    unittest.main()
