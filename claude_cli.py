import asyncio
import json
from enum import Enum
from typing import List, Optional, Tuple


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

    def build_command(self, prompt: str, mode: Mode, session_id: Optional[str] = None) -> List[str]:
        cmd = ["claude", "-p", "--output-format", "json"]

        if mode == Mode.WRITE:
            cmd += ["--allowedTools", "Write", "Edit"]
        elif mode == Mode.FULL:
            cmd.append("--dangerously-skip-permissions")

        if session_id:
            cmd += ["--resume", session_id]

        cmd.append(prompt)
        return cmd

    def parse_response(self, raw: str) -> Tuple[str, Optional[str]]:
        try:
            data = json.loads(raw)
            return data.get("result", ""), data.get("session_id")
        except (json.JSONDecodeError, KeyError):
            return raw.strip(), None

    async def _execute(self, cmd: List[str], timeout: int = 300) -> Tuple[str, str]:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.work_dir,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            raise
        return stdout.decode(), stderr.decode()

    async def run(self, prompt: str, mode: Mode, session_id: Optional[str] = None) -> Tuple[str, Optional[str]]:
        cmd = self.build_command(prompt, mode, session_id)
        stdout, stderr = await self._execute(cmd)

        if not stdout.strip() and stderr.strip():
            return f"Error: {stderr.strip()}", session_id

        return self.parse_response(stdout)
