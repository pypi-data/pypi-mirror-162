import threading
from collections import defaultdict
from typing import Any, DefaultDict, Generic

from checksum_dict.base import AnyAddressOrContract, ChecksumAddressDict, T


_LocksDict = DefaultDict[AnyAddressOrContract, threading.Lock]

class ChecksumAddressSingletonMeta(type, Generic[T]):
    __locks: _LocksDict = defaultdict(threading.Lock)
    __locks_lock: threading.Lock = threading.Lock()
    __instances: ChecksumAddressDict[T] = ChecksumAddressDict()

    def __call__(self, address: AnyAddressOrContract, *args: Any, **kwargs: Any) -> T:  # type: ignore
        address = str(address)
        try:
            instance = self.__instances[address]
        except KeyError:
            with self.__get_address_lock(address):
                # Try to get the instance again, in case it was added while waiting for the lock
                try:
                    instance =  self.__instances[address]
                except KeyError:
                    instance = super().__call__(address, *args, **kwargs)
                    self.__instances[address] = instance
            self.__delete_address_lock(address)
        return instance
    
    def __get_address_lock(self, address: AnyAddressOrContract) -> threading.Lock:
        """ Makes sure the singleton is actually a singleton. """
        with self.__locks_lock:
            return self.__locks[address]
    
    def __delete_address_lock(self, address: AnyAddressOrContract) -> None:
        """ No need to maintain locks for initialized addresses. """
        with self.__locks_lock:
            try:
                del self.__locks[address]
            except KeyError:
                pass
