"""Tests for exception_logger helpers."""

import inspect

import pytest

from resources.lib import exception_logger


def test_format_vars_filters_and_sorts():
    variables = {"__ignored__": 1, "b": 2, "a": 1}
    formatted = exception_logger._format_vars(variables)
    assert formatted.splitlines() == ["a = 1", "b = 2"]


def _sample_frame_info():
    value = "marker"
    frame = inspect.currentframe()
    # Keep locals alive for _format_frame_info
    assert value == "marker"
    return (
        frame,
        frame.f_code.co_filename,
        frame.f_lineno,
        frame.f_code.co_name,
        ["value = 'marker'\n"],
        0,
    )


def test_format_code_context_marks_current_line():
    info = _sample_frame_info()
    context = exception_logger._format_code_context(info)
    assert ">" in context
    assert str(info[2]) in context


def test_format_frame_info_includes_locals():
    info = _sample_frame_info()
    formatted = exception_logger._format_frame_info(info)
    assert "File:" in formatted
    assert "Local variables:" in formatted
    assert "value = 'marker'" in formatted


def test_log_exception_emits_diagnostic_and_reraises(monkeypatch):
    messages = []

    def _logger(msg):
        messages.append(msg)

    fake_info = _sample_frame_info()
    monkeypatch.setattr(exception_logger.inspect, "trace", lambda *a, **k: [fake_info])

    with pytest.raises(RuntimeError):
        with exception_logger.log_exception(logger_func=_logger):
            raise RuntimeError("boom")

    assert messages
    assert "Unhandled exception detected" in messages[0]
    assert "RuntimeError" in messages[0]
