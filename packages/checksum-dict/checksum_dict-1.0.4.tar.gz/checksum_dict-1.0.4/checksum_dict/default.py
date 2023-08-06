from collections import defaultdict
from typing import Callable, Iterable

from checksum_dict._key import EthAddressKey
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
    
    def _getitem_nochecksum(self, key: EthAddressKey) -> T:
        """
        You can use this method in custom subclasses to bypass the checksum ONLY if you know its already been done at an earlier point in your code.
        """
        if key in self:
            return self[key]
        default = self.default_factory()  # type: ignore
        dict.__setitem__(self, key, default)
        return default
    
    def _setitem_nochecksum(self, key: EthAddressKey, value: T) -> None:
        """
        You can use this method in custom subclasses to bypass the checksum ONLY if you know its already been done at an earlier point in your code.
        """
        if not key.startswith("0x") or len(key) != 42:
            raise ValueError(f"'{key}' is not a valid ETH address")
        dict.__setitem__(self, key, value)
