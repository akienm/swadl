"""Tests for SWADLBaseAutomation.stopwatch() and .logger perf integration."""

from __future__ import annotations

import csv
from pathlib import Path

from diagnostic_base.perf import Stopwatch
from diagnostic_base.tagged_logger import TaggedLogger

from SWADL.engine.swadl_base_automation import SWADLBaseAutomation


class _Noop(SWADLBaseAutomation):
    pass


class TestStopwatch:
    def test_returns_stopwatch_instance(self, tmp_path):
        obj = _Noop()
        sw = obj.stopwatch("op", log_root=tmp_path)
        assert isinstance(sw, Stopwatch)

    def test_device_id_is_lowered_class_name(self, tmp_path):
        obj = _Noop()
        sw = obj.stopwatch("op", log_root=tmp_path)
        assert sw.device_id == "_noop"

    def test_class_name_bound(self, tmp_path):
        obj = _Noop()
        sw = obj.stopwatch("op", log_root=tmp_path)
        assert sw.class_name == "_Noop"

    def test_context_manager_success(self, tmp_path):
        obj = _Noop()
        with obj.stopwatch("timed_op", log_root=tmp_path) as t:
            pass
        assert t.success is True
        assert t.elapsed_s >= 0

    def test_csv_row_written(self, tmp_path):
        obj = _Noop()
        with obj.stopwatch("csv_op", log_root=tmp_path):
            pass
        perf_dir = tmp_path / "_noop" / "perf"
        csv_files = list(perf_dir.glob("*.perf.csv"))
        assert len(csv_files) == 1
        rows = list(csv.DictReader(csv_files[0].open()))
        assert rows[0]["stopwatch_id"] == "csv_op"
        assert rows[0]["device_id"] == "_noop"


class TestLoggerProperty:
    def test_logger_is_tagged_logger(self):
        obj = _Noop()
        assert isinstance(obj.logger, TaggedLogger)

    def test_perf_tag_accessible(self):
        obj = _Noop()
        perf = obj.logger.perf
        assert callable(perf)

    def test_logger_shared_across_instances(self):
        a = _Noop()
        b = _Noop()
        assert a.logger is b.logger
