from __future__ import annotations

import json
import os
from functools import cached_property
from typing import Optional, Callable, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from terrascript.core.lang.types import Out, Schema, Collection
    from terrascript.core.lang.block import Block

from pydash import pull

from .generate import Generator
from .cmd import Terraform


class Runner:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self._generator = Generator(self.ctx.path, blocks=self.ctx.blocks)
        self._tf = Terraform(path=self.ctx.path)
        self._workspace: Optional[str] = None

    async def prepare(self):
        self.ctx.register_exports()
        self._generator.generate()

        await self._tf.format()
        await self._tf.init()
        if self._workspace:
            await self._tf.workspace(self._workspace)

    async def apply(self):
        from terrascript.core.lang.output import process_outputs

        await self.prepare()
        await self._tf.apply()

        rc, stdout = await self._tf.output()
        if rc == 0 and stdout:
            process_outputs(self.ctx.export_blocks, json.loads(stdout))

    async def plan(self):
        await self.prepare()
        await self._tf.plan()

    async def destroy(self):
        await self.prepare()
        await self._tf.destroy()

    def workspace(self, name: str):
        self._workspace = name

    def stdout(self, cb: Callable[[bytes], int]):
        self._tf.stdout(cb)


class Context:
    def __init__(self, *, path: Optional[str] = None):
        self._path = path
        self._blocks = []
        self._exports = []
        self._exportBlocks = []
        self._runner = Runner(self)

    @cached_property
    def path(self):
        return self._path if self._path else os.path.join(os.getcwd(), ".terrascript")

    @property
    def blocks(self):
        return self._blocks

    @property
    def export_blocks(self):
        return self._exportBlocks

    @property
    def exports(self):
        return self._exports

    def register(self, block: Block):
        self._blocks.append(block)

    def unregister(self, block: Block):
        pull(self._blocks, block)

    async def apply(self):
        await self._runner.apply()

    async def plan(self):
        await self._runner.plan()

    async def destroy(self):
        await self._runner.destroy()

    def workspace(self, name) -> Context:
        self._runner.workspace(name)
        return self

    def export(self, exp: Out):
        out = self._traverse(exp)
        if out:
            self._exports.append(out)
            self._exportBlocks.append(out.parent)

    def stdout(self, cb: Callable[[bytes], int]):
        self._runner.stdout(cb)

    @classmethod
    def _traverse(cls, exp: Out) -> Optional[Out]:
        from terrascript.core.lang.types import (
            is_schema,
            is_collection,
            is_out,
            Out,
            Collection,
        )

        from terrascript.core.lang.block import is_configuration

        out = None
        if is_schema(exp):
            out = cast(Schema, exp).out_()
        elif is_collection(exp):
            out = cast(Collection, exp).item
        elif is_out(exp):
            out = cast(Out, exp)

        if out and out.parent:
            if is_configuration(out.parent):
                return out
            else:
                parent = out.parent.out_()
                if parent:
                    cls._traverse(parent)

        return None

    def register_exports(self):
        from terrascript.core.lang.types import is_schema
        from terrascript.core.lang.output import Output

        for exp in self._exports:
            if is_schema(exp):
                exp = exp.out_()

            Output(
                name=f"{exp.parent.type_}-{exp.parent.name_}-{exp.attr.name}",
                value=f"${{{exp.expr_()}}}",
            )


ctx = Context()


def register_block(block: Block):
    ctx.register(block)


def unregister_block(block: Block):
    ctx.unregister(block)


async def apply():
    await ctx.apply()


async def plan():
    await ctx.plan()


async def destroy():
    await ctx.destroy()


def workspace(name: str) -> Context:
    ctx.workspace(name)
    return ctx


def export(out: Out):
    ctx.export(out)


def stdout(cb: Callable[[bytes], int]) -> Context:
    ctx.stdout(cb)
    return ctx
