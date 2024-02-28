
from .common import Descriptor
from .common.utils import package_name


class Automatic:
    def __init__(self, contexts):
        self.__contexts = contexts


    def _context(self, desc:Descriptor):
        for ctx in self.__contexts:
            if package_name(desc) == package_name(ctx):
                return ctx
        return None


    def _dispatch(self, context, op, *args, **kwargs):
        if not context:
            # NoContextException
            return False
        op = getattr(context, op, None)
        if not op:
            # NotSupportedOperation
            return False

        return op(*args, **kwargs)


    def _do(self, op, desc:Descriptor, *args, **kwargs):
        # dispatch context for a descriptor
        ctx = self._context(desc)
        if not ctx:
            # NoContextException
            return False

        # Run operation in a context
        return self._dispatch(ctx, op, desc, *args, **kwargs)
    
    def _get(self, op, desc:Descriptor, *args, **kwargs):
         # dispatch context for a descriptor
        ctx = self._context(desc)
        if not ctx:
            # NoContextException
            return None

        # Run operation in a context
        return self._dispatch(ctx, op, desc, *args, **kwargs)


    def exist(self, desc:Descriptor):
        return self._do("exist", desc)


    def go(self, desc:Descriptor):
        return self._do("go", desc)


    def click(self, target:Descriptor):
        return self._do("click", target)


    def clicks(self, target:Descriptor, *, num_samples=None):
        return self._do("clicks", target, num_samples=num_samples)

    def type(self, desc:Descriptor, text):
        return self._do("type", desc, text)


    def table(self, desc:Descriptor):
        return self._get("table", desc)
    
    def accept(self, target:Descriptor):
        return self._do("accept", target )
    
    def select(self, target:Descriptor, text:str):
        return self._do("select", target, text)
