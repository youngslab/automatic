

import time
from abc import ABC, abstractmethod
from .descriptor import Descriptor

class Context():
    def __init__(self):
        self.__differ = 0

    def wait(self, desc: Descriptor):
        differ = desc.differ()
        differ = differ if differ else self.__differ
        if differ != 0:
            time.sleep(differ)