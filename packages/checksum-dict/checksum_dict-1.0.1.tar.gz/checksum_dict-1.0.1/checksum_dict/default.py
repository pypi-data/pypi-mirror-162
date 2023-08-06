from collections import defaultdict
from typing import Callable, Iterable

from checksum_dict.base import ChecksumAddressDict, T, _SeedT


class DefaultChecksumDict(defaultdict, ChecksumAddressDict[T]):
    """
    A defaultdict that maps addresses to objects.
    Will automatically checksum your provided address key when setting and getting values.
    """
    def __init__(self, default: Callable[[], T], seed: _SeedT = None) -> None:
        super().__init__(default)
        self.__dict__ = self
        if isinstance(seed, dict):
            seed = seed.items()
        if isinstance(seed, Iterable):
            for key, value in seed:
                self[key] = value
    