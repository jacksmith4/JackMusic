import pytest
from datetime import datetime, timedelta
from pathlib import Path
import importlib


def load_function_module():
    import sys, os
    settings = Path("settings.json")
    if not settings.exists():
        settings.write_text("{}")
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    return importlib.import_module("function")


def make_entry(days_ago: int, idx: int) -> dict:
    return {
        "track_id": f"track{idx}",
        "timestamp": (datetime.utcnow() - timedelta(days=days_ago)).timestamp(),
    }


def test_prune_by_age():
    mod = load_function_module()
    history = [make_entry(40, i) for i in range(10)] + [make_entry(10, i) for i in range(5)]
    pruned = mod.prune_history(history)
    assert all(
        datetime.fromtimestamp(item["timestamp"]) >= datetime.utcnow() - timedelta(days=mod.HISTORY_RETENTION_DAYS)
        for item in pruned
    )
    assert len(pruned) == 5


def test_prune_by_length():
    mod = load_function_module()
    history = [make_entry(0, i) for i in range(mod.HISTORY_MAX_ENTRIES + 20)]
    pruned = mod.prune_history(history)
    assert len(pruned) == mod.HISTORY_MAX_ENTRIES
    assert pruned == history[-mod.HISTORY_MAX_ENTRIES:]
