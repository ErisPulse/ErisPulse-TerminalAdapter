"""基线协议回归：终端适配器元动作标准形状"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from TerminalAdapter.Core import TerminalAdapter


def test_get_version_contains_onebot_version():
    adapter = TerminalAdapter()
    result = asyncio.run(adapter.call_api("get_version"))
    assert result["status"] == "ok"
    assert "onebot_version" in result["data"]
    assert result["data"]["version"]


def test_get_status_and_supported_actions():
    adapter = TerminalAdapter()
    status = asyncio.run(adapter.call_api("get_status"))
    assert status["status"] == "ok"
    assert "enabled" in status["data"] and "boot_time" in status["data"]

    actions = asyncio.run(adapter.call_api("get_supported_actions"))
    assert isinstance(actions["data"], list) and "send_message" in actions["data"]


def test_delete_message_unsupported():
    adapter = TerminalAdapter()
    result = asyncio.run(adapter.call_api("delete_message", message_id="x"))
    assert result["status"] == "failed"
    assert result["retcode"] == 10002
