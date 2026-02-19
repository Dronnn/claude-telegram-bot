import json
from unittest.mock import AsyncMock, patch

import pytest

from claude_cli import ClaudeCLI, Mode


def test_mode_enum():
    assert Mode.SAFE.value == "safe"
    assert Mode.WRITE.value == "write"
    assert Mode.FULL.value == "full"


def test_build_command_safe_no_session():
    cli = ClaudeCLI(work_dir="/tmp/test")
    cmd = cli.build_command("hello", mode=Mode.SAFE, session_id=None)
    assert cmd == ["claude", "-p", "--output-format", "json", "hello"]


def test_build_command_write_mode():
    cli = ClaudeCLI(work_dir="/tmp/test")
    cmd = cli.build_command("hello", mode=Mode.WRITE, session_id=None)
    assert "--allowedTools" in cmd
    assert "Write" in cmd
    assert "Edit" in cmd


def test_build_command_full_mode():
    cli = ClaudeCLI(work_dir="/tmp/test")
    cmd = cli.build_command("hello", mode=Mode.FULL, session_id=None)
    assert "--dangerously-skip-permissions" in cmd


def test_build_command_with_session():
    cli = ClaudeCLI(work_dir="/tmp/test")
    cmd = cli.build_command("hello", mode=Mode.SAFE, session_id="abc-123")
    assert "--resume" in cmd
    assert "abc-123" in cmd


def test_parse_response_json():
    cli = ClaudeCLI(work_dir="/tmp/test")
    raw = json.dumps({"result": "Hello!", "session_id": "sess-1"})
    text, session_id = cli.parse_response(raw)
    assert text == "Hello!"
    assert session_id == "sess-1"


def test_parse_response_plain_text():
    cli = ClaudeCLI(work_dir="/tmp/test")
    text, session_id = cli.parse_response("Just plain text")
    assert text == "Just plain text"
    assert session_id is None


@pytest.mark.asyncio
async def test_run_returns_text_and_session():
    cli = ClaudeCLI(work_dir="/tmp/test")
    mock_result = json.dumps({"result": "Hi!", "session_id": "s-1"})

    with patch.object(cli, "_execute", new_callable=AsyncMock, return_value=(mock_result, "")):
        text, session_id = await cli.run("hello", mode=Mode.SAFE)
        assert text == "Hi!"
        assert session_id == "s-1"
