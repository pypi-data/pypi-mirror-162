"""Formulas for the Humanitarian Exchange Language (HXL).

Formulas operate horizontally across a row, so that they use constant memory in a large dataset.
"""

import abc

class AbstractValue(object):

    __metaclass__ = abc.ABCMeta

    @abstractmethod
    @property
    def value(self):
        return

class Constant(AbstractValue):
    """Constant value in a formula (string, number, or date)."""

    def __construct__(self, v):
        self.__value__ = v

    def value(self):
        return self.__value__
    

class Function(AbstractValue):

    def __construct__(self, op, params=[]):
        """Create a function.
        @param op: a lambda expression that takes two parameters and reduces them to one.
        @param params: a list of AbstractValue objects.
        """
        self.__params__ = params

    def apply(self):
        """Apply the function to its parameters.
        """
        result = ''
        
        if self.params:
            result = params[0].value
            for param in params[1:]:
                result = self.op(result, param.value)

        return result
