from typing import List
import time
from .data_types.owl_function import OwlCallable


class ClockFunction(OwlCallable):
    def call(self, interpreter, arguments: List):
        return time.time()

    def arity(self) -> int:
        return 0

    def __str__(self):
        return "<native clock fn>"


class NumberFunction(OwlCallable):
    def call(self, interpreter, arguments: List):
        return float(arguments[0])

    def arity(self) -> int:
        return 1

    def __str__(self):
        return "<native number fn>"


class InputFunction(OwlCallable):
    def call(self, interpreter, arguments: List):
        return input(arguments[0])

    def arity(self) -> int:
        return 1

    def __str__(self):
        return "<native input fn>"
