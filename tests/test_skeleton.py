# -*- coding: utf-8 -*-

import pytest
from wapor.skeleton import fib

__author__ = "Quan Pan"
__copyright__ = "Quan Pan"
__license__ = "apache"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13

    with pytest.raises(AssertionError):
        fib(-10)
