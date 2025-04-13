from .descriptor import Descriptor

class AutomaticException(Exception):
    def __init__(self, context, desc: Descriptor, op=None, message="An error occurred."):
        self.message = message
        self.context = context
        self.desc = desc
        self.op = op
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}. op={self.op}, desc={self.desc}'

class InvalidOperationException(AutomaticException):
    def __init__(self, context, desc: Descriptor, op, message="Operation is not supported."):
        super().__init__(context, desc, op, message)

class ActivationFailureException(AutomaticException):
    def __init__(self, context, desc: Descriptor, message="Activation Failure"):
        super().__init__(context, desc, None, message)

class OperationFailureException(AutomaticException):
    def __init__(self, context, desc: Descriptor, op, message="Operation failed."):
        super().__init__(context, desc, op, message)

class ElementNotFoundException(AutomaticException):
    def __init__(self, context, desc: Descriptor, op, message="Element is not Found."):
        super().__init__(context, desc, op, message)


