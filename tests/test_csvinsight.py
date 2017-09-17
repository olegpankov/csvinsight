#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `csvinsight` package."""

import io

import pytest

from click.testing import CliRunner

from csvinsight import csvinsight
from csvinsight import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


@pytest.mark.skip('not implemented yet')
def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'csvinsight.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_reduce():
    buf = io.BytesIO(b'1\n2\n3\n')
    summary = csvinsight.reduce(buf)
    assert summary['num_fills'] == 3

    buf = io.BytesIO(b'\n\n3\n')
    summary = csvinsight.reduce(buf)
    assert summary['num_fills'] == 1

    buf = io.BytesIO(b'foo\n')
    summary = csvinsight.reduce(buf)
    assert summary['most_common'] == [(1, b'foo')]


def test_top_n():
    topn = csvinsight.TopN(limit=3)
    topn.push(1, 'foo')
    topn.push(2, 'bar')
    topn.push(3, 'baz')
    assert topn.to_list() == [(1, 'foo'), (2, 'bar'), (3, 'baz')]

    topn.push(4, 'boz')
    assert topn.to_list() == [(2, 'bar'), (3, 'baz'), (4, 'boz')]

    topn.push(1, 'oops')
    assert topn.to_list() == [(2, 'bar'), (3, 'baz'), (4, 'boz')]


def never_close(stream):
    stream.close = lambda: None
    return stream


def test_column_splitter():
    open_file = lambda column_name: never_close(io.BytesIO())
    header = ['foo', 'bar']
    list_fields = ['bar']
    lines = [b'1|2;3\n', b'4|5;6\n']
    splitter = csvinsight.ColumnSplitter(header, open_file, list_fields=list_fields)
    for line in lines:
        splitter.split_line(line)

    assert splitter._fout['foo'].getvalue() == b'1\n4\n'
    assert splitter._fout['bar'].getvalue() == b'2\n3\n5\n6\n'
