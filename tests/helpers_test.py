import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logic.helpers.common import generate_pagination

def lists_equal(l1: list, l2: list) -> bool:
    if len(l1) != len(l2):
        return False
    for i in range(len(l1)):
        if l1[i] != l2[i]:
            return False
    return True

def test_pagination_1():
    pages = generate_pagination(8, 9, 3)
    assert lists_equal(pages, list(range(1, 9)))

def test_pagination_2():
    expected = [1] + list(range(11, 16)) + [20]
    pages = generate_pagination(20, 7, 13)
    assert lists_equal(pages, expected)

def test_pagination_3():
    expected = list(range(1, 8)) + [20]
    pages = generate_pagination(20, 8, 2)
    assert lists_equal(pages, expected)

def test_pagination_4():
    expected = [1] + list(range(11, 21))
    pages = generate_pagination(20, 11, 17)
    assert lists_equal(pages, expected)
