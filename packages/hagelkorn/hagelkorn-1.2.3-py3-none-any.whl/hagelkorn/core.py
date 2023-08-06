import datetime
import random as rnd
import typing

DEFAULT_ALPHABET = "13456789ABCDEFHKLMNPQRTWXYZ"


class Resolution:
    """Helper type for specifying minimum time resolutions."""

    microseconds = 1e-6
    milliseconds = 1e-3
    seconds = 1
    minutes = 60
    hours = 3600
    days = 86400


def key_length(
    overflow_years: float, resolution: float, B: int
) -> typing.Tuple[int, int, float]:
    """
    Determines some key parameters for ID generation.

    Parameters
    ----------
    overflow_years : float
        Number of years after which the key length will be exceeded
    resolution : float
        Maximum length of an interval (in seconds)
    B : int
        Base of the positional notation (length of alphabet)

    Returns
    -------
    D : int
        Number of digits of the ID
    K : int
        Total number of unique IDs (intervals)
    T : float
        Duration of one interval in seconds
    """
    total_seconds = overflow_years * 31536000
    K_min = total_seconds / resolution
    D = 1
    K = B
    while K < K_min:
        D += 1
        K *= B
    T = total_seconds / K
    return D, K, T


def base(n: float, alphabet: str, digits: int) -> str:
    """
    Converts a real-valued number into its baseN-notation.

    Parameters
    ----------
    n : float
        Number to be converted (decimal precision will be droped)
    alphabet : str
        Alphabet of the positional notation system
    digits : int
        Number of digits in the ID

    Returns
    -------
    id : str
        Length may exceed the specified number of digits
        if n results in an overflow
    """
    B = len(alphabet)
    output = ""
    while n > 0:
        output += alphabet[int(n) % B]
        n = n // B
    return output[::-1].rjust(digits, alphabet[0])


class HagelSource:
    """An ID-generator that exposes some internal parameters."""

    def __init__(
        self,
        resolution: float = Resolution.seconds,
        alphabet: str = DEFAULT_ALPHABET,
        start: datetime.datetime = datetime.datetime(
            2018, 1, 1, tzinfo=datetime.timezone.utc
        ),
        overflow_years: float = 10,
    ):
        """Creates an ID-generator that is slightly faster and a bit more transparent.

        Parameters
        ----------
        resolution : float
            Maximum duration in seconds for an increment in the id
        alphabet : str
            The (sorted) characters to be used in the ID generation
        start : datetime
            Beginning of timeline
        overflow_years : float
            Number of years after which the key length will increase by 1
        """
        self.alphabet = alphabet
        self.B = len(alphabet)
        self.start = start.astimezone(datetime.timezone.utc)
        self.total_seconds = overflow_years * 31536000
        self.end = self.start + datetime.timedelta(self.total_seconds / 86400)

        self.digits, self.combinations, self.resolution = key_length(
            overflow_years, resolution, self.B
        )

        super().__init__()

    def monotonic(self, now: typing.Optional[datetime.datetime] = None) -> str:
        """
        Generates a short, human-readable ID that
        increases monotonically with time.

        Parameters
        ----------
        now : datetime
            Timpoint at which the ID is generated

        Returns
        -------
        id : str
            The generated hagelkorn
        """
        if now is None:
            now = datetime.datetime.utcnow()

        elapsed_seconds = (
            now.astimezone(datetime.timezone.utc) - self.start
        ).total_seconds()
        elapsed_intervals = int(elapsed_seconds / self.resolution)

        return base(elapsed_intervals, self.alphabet, self.digits)


def monotonic(
    resolution: float = Resolution.seconds,
    now: typing.Optional[datetime.datetime] = None,
    alphabet: str = DEFAULT_ALPHABET,
    start: datetime.datetime = datetime.datetime(
        2018, 1, 1, tzinfo=datetime.timezone.utc
    ),
    overflow_years: float = 10,
) -> str:
    """
    Generates a short, human-readable ID that
    increases monotonically with time.

    Parameters
    ----------
    resolution : float
        Maximum duration in seconds for an increment in the id
    now : datetime
        Timpoint at which the ID is generated
    alphabet : str
        The (sorted) characters to be used in the ID generation
    start : datetime
        Beginning of timeline
    overflow_years : float
        Number of years after which the key length will increase by 1

    Returns
    -------
    id : str
        The generated hagelkorn
    """
    # clean up input arguments
    start = start.astimezone(datetime.timezone.utc)
    if now is None:
        now = datetime.datetime.utcnow()

    # find parameters
    B = len(alphabet)
    digits, combis, resolution = key_length(overflow_years, resolution, B)

    # find the interval number
    elapsed_s = (now.astimezone(datetime.timezone.utc) - start).total_seconds()
    elapsed_intervals = int(elapsed_s / resolution)

    # encode
    return base(elapsed_intervals, alphabet, digits)


def random(digits: int = 5, alphabet: str = DEFAULT_ALPHABET) -> str:
    """
    Generates a random alphanumberic ID.

    Parameters
    ----------
    digits : int
        Length of the generated ID
    alphabet : str
        Available characters for the ID

    Returns
    -------
    id : str
        The generated hagelkorn
    """
    return "".join(rnd.choices(alphabet, k=digits))
