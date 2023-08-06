from typing import TYPE_CHECKING, Dict, Iterable, Tuple, TypeVar, Union

from checksum_dict._key import EthAddressKey

if TYPE_CHECKING:
    from checksum_dict._key import AnyAddressOrContract
else:
    from eth_typing import AnyAddress as AnyAddressOrContract


T = TypeVar("T")

_SeedT = Union[Dict[AnyAddressOrContract, T], Iterable[Tuple[AnyAddressOrContract, T]]]

class ChecksumAddressDict(Dict[EthAddressKey, T]):
    """
    A dict that maps addresses to objects.
    Will automatically checksum your provided address key when setting and getting values.
    If you pass in a `seed` dictionary, the keys will be checksummed and the values will be set.
    """
    def __init__(self, seed: _SeedT = None) -> None:
        super().__init__()
        self.__dict__ = self
        if isinstance(seed, dict):
            seed = seed.items()
        if isinstance(seed, Iterable):
            for key, value in seed:
                self[key] = value
    
    def __repr__(self) -> str:
        return f"ChecksumAddressDict({str(dict(self))})"
    
    def __getitem__(self, key: AnyAddressOrContract) -> T:
        return super().__getitem__(EthAddressKey(key))
    
    def __setitem__(self, key: AnyAddressOrContract, value: T) -> None:
        return super().__setitem__(EthAddressKey(key), value)
