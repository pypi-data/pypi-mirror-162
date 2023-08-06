#!/usr/bin/env python

"""Tests for `razator_utils` package."""
from pathlib import Path

from razator_utils import batchify, camel_to_snake, log


def test_camel_to_snake():
    """Test the camel_to_snake function which converts camelCase to snake_case"""
    assert camel_to_snake('thisIsTest') == 'this_is_test'
    assert camel_to_snake('anotherATest') == 'another_a_test'


def test_batchify():
    iterable = ['a', 'b', 'c', 'd', 'e']
    assert [x for x in batchify(iterable, 2)] == [['a', 'b'], ['c', 'd'], ['e']]


def test_stout_log():
    logger = log.get_stout_logger('pytest.py', 'INFO')
    assert logger.level == 20
    log_file = Path('test.log')
    file_logger = log.get_file_logger('pytest_file_log.py', log_file, 'WARNING')
    file_logger.warning('This is a warning')
    assert log_file.exists()
    log_file.unlink()
