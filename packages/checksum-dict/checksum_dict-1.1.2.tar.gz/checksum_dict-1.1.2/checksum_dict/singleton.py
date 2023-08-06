import threading
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Generic, Tuple

from checksum_dict.base import AnyAddressOrContract, ChecksumAddressDict, T


_LocksDict = DefaultDict[AnyAddressOrContract, threading.Lock]

class ChecksumAddressSingletonMeta(type, Generic[T]):
    def __init__(cls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        cls.__instances: ChecksumAddressDict[T] = ChecksumAddressDict()
        cls.__locks: _LocksDict = defaultdict(threading.Lock)
        cls.__locks_lock: threading.Lock = threading.Lock()

    def __call__(cls, address: AnyAddressOrContract, *args: Any, **kwargs: Any) -> T:  # type: ignore
        address = str(address)
        try:
            instance = cls.__instances[address]
        except KeyError:
            with cls.__get_address_lock(address):
                # Try to get the instance again, in case it was added while waiting for the lock
                try:
                    instance =  cls.__instances[address]
                except KeyError:
                    instance = super().__call__(address, *args, **kwargs)
                    cls.__instances[address] = instance
            cls.__delete_address_lock(address)
        return instance
    
    def __get_address_lock(cls, address: AnyAddressOrContract) -> threading.Lock:
        """ Makes sure the singleton is actually a singleton. """
        with cls.__locks_lock:
            return cls.__locks[address]
    
    def __delete_address_lock(cls, address: AnyAddressOrContract) -> None:
        """ No need to maintain locks for initialized addresses. """
        with cls.__locks_lock:
            try:
                del cls.__locks[address]
            except KeyError:
                pass
