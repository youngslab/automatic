

from abc import ABC, abstractmethod
from ..common import Descriptor
from enum import Enum

# TODO: classmethod?

class DefaultFrame(Descriptor):
    def __init__(self):
        super().__init__("", "", parent=None)

    def by(self) -> str:
        return "default frame"

class DefaultFrameDescriptor(Descriptor, ABC):
    def __init__(self, desc, path, *, parent: Descriptor = DefaultFrame(),
                 timeout=None, differ=0):
        super().__init__(desc, path, parent=parent, timeout=timeout, differ=differ)

# Element Descriptor
class Xpath(DefaultFrameDescriptor):
    class Order(Enum):
        Random = 1
        FromStart = 2
        FromEnd = 3

    def __init__(self, desc, path, *, parent: Descriptor = DefaultFrame(),
                 timeout=None, differ=0, multiple=False, sample=0, order=Order.FromStart, visible=True):
        super().__init__(desc, path, parent=parent, timeout=timeout, differ=differ)
        self.multiple=multiple
        self.sample = sample
        self.order = order
        self.visible = visible

    def by(self) -> str:
        return "xpath"


class Id(DefaultFrameDescriptor):
    def by(self) -> str:
        return "id"


class Name(DefaultFrameDescriptor):
    def by(self) -> str:
        return "name"


# Non-Element Descriptor
class Title(Descriptor):
    def by(self) -> str:
        return "title"


class Url(Descriptor):
    def by(self) -> str:
        return "url"


class Alert(Descriptor):
    def by(self) -> str:
        return "alert"

class Handle(Descriptor):
    def by(self) -> str:
        return "handle"


def is_element(desc:Descriptor) -> bool:
    return desc.by() in ["xpath", "id", "name"]

def is_window(desc:Descriptor) -> bool:
    return desc.by() in ["url", "title" ]

def is_alert(desc:Descriptor) -> bool:
    return desc.by() in ["alert"]

def is_default_frame(desc:Descriptor) -> bool:
    return desc.by() in ["default frame"]

"""
    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"
"""

