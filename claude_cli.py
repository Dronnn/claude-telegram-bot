import asyncio
import json
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class Mode(Enum):
    SAFE = "safe"
    WRITE = "write"
    FULL = "full"


MODE_LABELS = {
    Mode.SAFE: "Только чтение",
    Mode.WRITE: "Запись (Write + Edit)",
    Mode.FULL: "Полный доступ",
}


class ClaudeCLI:
    def __init__(self, work_dir: str):
        self.work_dir = work_dir

    def build_command(self, mode: Mode, session_id: Optional[str] = None) -> List[str]:
        cmd = ["claude", "-p", "--output-format", "json"]

        if mode == Mode.SAFE:
            cmd += ["--allowedTools", "Read,LS,Glob,Grep"]
        elif mode == Mode.WRITE:
            cmd += ["--allowedTools", "Read,Write,Edit,Bash,LS,Glob,Grep"]
        elif mode == Mode.FULL:
            cmd.append("--dangerously-skip-permissions")

        if session_id:
            cmd += ["--resume", session_id]

        return cmd

    def parse_stats(self, raw: str) -> Dict[str, Any]:
        """Extract usage stats from CLI JSON response."""
        stats = {}  # type: Dict[str, Any]
        try:
            data = json.loads(raw)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("type") == "result":
                    for key in ("cost_usd", "num_turns", "duration_ms", "duration_api_ms"):
                        if key in item:
                            stats[key] = item[key]
        except (json.JSONDecodeError, TypeError):
            pass
        return stats

    def parse_response(self, raw: str) -> Tuple[str, Optional[str]]:
        try:
            data = json.loads(raw)

            # Single object: {"result": "...", "session_id": "..."}
            if isinstance(data, dict):
                return data.get("result") or "", data.get("session_id")

            # Array of objects: find the "result" entry
            if isinstance(data, list):
                result_text = ""
                session_id = None
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "result":
                        result_text = item.get("result") or ""
                        session_id = item.get("session_id")
                        break
                    if "session_id" in item and not session_id:
                        session_id = item["session_id"]
                # Fallback: extract text from message content blocks
                if not result_text:
                    texts = []
                    for item in data:
                        if not isinstance(item, dict):
                            continue
                        msg = item.get("message", {})
                        if isinstance(msg, dict):
                            for block in msg.get("content", []):
                                if isinstance(block, dict) and block.get("type") == "text":
                                    texts.append(block["text"])
                    result_text = "\n".join(texts)
                return result_text, session_id

            return raw.strip(), None
        except (json.JSONDecodeError, KeyError, TypeError):
            return raw.strip(), None

    async def _execute(self, cmd: List[str], stdin_data: Optional[str] = None, timeout: int = 300) -> Tuple[str, str]:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if stdin_data else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.work_dir,
        )
        try:
            stdin_bytes = stdin_data.encode() if stdin_data else None
            stdout, stderr = await asyncio.wait_for(proc.communicate(input=stdin_bytes), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            raise
        return stdout.decode(), stderr.decode()

    async def run(self, prompt: str, mode: Mode, session_id: Optional[str] = None) -> Tuple[str, Optional[str], Dict[str, Any]]:
        cmd = self.build_command(mode, session_id)
        stdout, stderr = await self._execute(cmd, stdin_data=prompt)

        logger.debug("CLI stdout: %s", stdout[:500])
        logger.debug("CLI stderr: %s", stderr[:500])

        if not stdout.strip() and stderr.strip():
            return f"Error: {stderr.strip()}", session_id, {}

        text, sid = self.parse_response(stdout)
        stats = self.parse_stats(stdout)
        return text, sid, stats
