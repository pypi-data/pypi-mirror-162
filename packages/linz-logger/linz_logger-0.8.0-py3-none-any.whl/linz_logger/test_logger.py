import json
import os

import pytest

from .logger import LogLevel, get_log, remove_contextvars, set_contextvars, set_level


def test_hello_without_name():
    """Test with no parameter."""
    assert get_log() is not None


def test_trace(capsys):
    """Test trace level"""
    set_level(LogLevel.trace)
    get_log().trace("abc")
    stdout, _ = capsys.readouterr()
    log = json.loads(stdout)
    assert log["level"] == 10
    assert log["msg"] == "abc"


def test_trace_at_debug_level(capsys):
    """Test trace level outputs nothing when log set to debug"""
    set_level(LogLevel.debug)
    get_log().trace("abc")
    stdout, _ = capsys.readouterr()
    assert stdout == ""


def test_timestamp(capsys):
    """Test timestamp is actually a timestamp"""
    set_level(LogLevel.trace)

    systime = int(os.popen("date +%s").read()) * 1000
    get_log().trace("abc")
    stdout, _ = capsys.readouterr()
    log = json.loads(stdout)

    assert log["time"] - systime < 1000


@pytest.mark.dependency()
def test_set_contextvars(capsys):
    set_contextvars({"hostname": "localhost", "ip": "192.168.0.2"})
    set_contextvars({"country": "NZ"})

    get_log().trace("abc")
    stdout, _ = capsys.readouterr()
    log = json.loads(stdout)

    assert log["hostname"] == "localhost"
    assert log["ip"] == "192.168.0.2"
    assert log["country"] == "NZ"


@pytest.mark.dependency(depends=["test_set_contextvars"])
def test_remove_contextvars(capsys):
    remove_contextvars(["hostname", "ip"])

    get_log().trace("def")
    stdout, _ = capsys.readouterr()
    log = json.loads(stdout)

    assert not "hostname" in log
    assert not "ip" in log
