import shutil
import asyncio
from functools import cached_property
from typing import Optional, Callable, List, Tuple


class CmdError(Exception):
    ...


async def _dequeue(
    stream: Optional[asyncio.StreamReader], cb: Optional[Callable[[bytes], None]] = None
):
    if not stream:
        return
    while True:
        line = await stream.readline()
        if not line:
            break
        if cb:
            cb(line)


async def _run(
    cmd: List[str],
    *,
    cwd=None,
    stdout: Optional[Callable[[bytes], None]] = None,
    stderr: Optional[Callable[[bytes], None]] = None,
    raise_on_error: bool = True,
) -> Optional[int]:
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )

    await asyncio.wait([_dequeue(process.stdout, stdout), _dequeue(process.stderr, stderr)])
    await process.communicate()
    await process.wait()

    rc = process.returncode
    if raise_on_error and rc != 0:
        raise CmdError(f"Problem running command {' '.join([s for s in cmd])}")

    return rc


class Terraform:
    def __init__(
        self,
        *,
        path: Optional[str] = None,
        cb: Optional[Callable[[bytes], None]] = None,
    ):
        self.path = path
        self._cb = cb
        self._out = bytearray()

        exe = shutil.which("terraform")
        if not exe:
            raise CmdError("Missing terraform installation")

        self._exe: str = exe

    def stdout(self, cb: Callable[[bytes], int]):
        self._cb = cb

    @cached_property
    def args(self):
        args = dict()
        if self.path:
            args["cwd"] = self.path
        return args

    def on_stdout(self, line: bytes):
        self._out.extend(line)
        if self._cb:
            self._cb(line)

    def on_stderr(self, line: bytes):
        self._out.extend(line)
        if self._cb:
            self._cb(line)

    def _reset(self):
        self._out.clear()

    async def init(self):
        self._reset()

        return await _run(
            [self._exe, "init"], stdout=self.on_stdout, stderr=self.on_stderr, **self.args
        )

    async def workspace(self, name: str):
        self._reset()

        await _run(
            [self._exe, "workspace", "new", name],
            stdout=self.on_stdout,
            stderr=self.on_stderr,
            raise_on_error=False,
            **self.args,
        )

        return await _run(
            [self._exe, "workspace", "select", name],
            stdout=self.on_stdout,
            stderr=self.on_stderr,
            **self.args,
        )

    async def plan(self):
        self._reset()

        return await _run(
            [self._exe, "plan"], stdout=self.on_stdout, stderr=self.on_stderr, **self.args
        )

    async def apply(self):
        self._reset()

        return await _run(
            [self._exe, "apply", "-auto-approve"],
            stdout=self.on_stdout,
            stderr=self.on_stderr,
            **self.args,
        )

    async def destroy(self):
        self._reset()

        return await _run(
            [self._exe, "apply", "-auto-approve", "-destroy"],
            stdout=self.on_stdout,
            stderr=self.on_stderr,
            **self.args,
        )

    async def format(self):
        self._reset()

        return await _run(
            [self._exe, "fmt", "-recursive"],
            stdout=self.on_stdout,
            stderr=self.on_stderr,
            **self.args,
        )

    async def output(self) -> Tuple[Optional[int], Optional[bytes]]:
        self._reset()

        rc = await _run(
            [self._exe, "output", "-json"],
            stdout=self.on_stdout,
            stderr=self.on_stderr,
            **self.args,
        )
        return rc, bytes(self._out) if rc == 0 else None
