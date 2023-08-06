'''
Author: acse-xy721 xy721@ic.ac.uk
Date: 2022-07-11 14:16:07
LastEditors: acse-xy721 xy721@ic.ac.uk
LastEditTime: 2022-08-08 20:59:21
FilePath: /YXYIPR/EnergyTerm.py
'''
import abc


class EnergyTerm():
    """EnergyTerm class
    The `EnergyTerm` class is an abstract base class that defines the `effective_field` method.
    The `@abc.abstractmethod` decorator tells Python that the `effective_field` method is an abstract
    method. This means that the `effective_field` method must be implemented by any class that inherits
    from `EnergyTerm`.
    """

    @abc.abstractmethod
    def effective_field(self, m):
        pass
