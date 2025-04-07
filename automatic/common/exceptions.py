
from .descriptor import Descriptor


class InvalidOperationException(Exception):
    def __init__(self, desc: Descriptor, op, message="Operation is not supported."):
        self.message = message
        self.desc = desc
        self.op
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}. op={self.op}, desc={self.desc}'



class ActivationFailureException(Exception):
    def __init__(self, desc: Descriptor):
        self.desc = desc
        super().__init__("Activation Failure")

    def __str__(self):
        return f'Activation Failure. desc={self.desc}'

class OperationFailureException(Exception):
    def __init__(self, desc: Descriptor, op, message="Operation failed."):
        self.message = message
        self.desc = desc
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}. op={self.op}, desc={self.desc}'
     

class ElementNotFoundException(Exception):
    def __init__(self, driver, desc: Descriptor, op , message="Element is not Found."):
        self.message = message
        self.desc = desc
        self.op = op
        self.driver = driver
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}. op={self.op}, desc={self.desc}'
    

