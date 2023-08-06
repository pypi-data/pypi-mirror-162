import os
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from terrascript.core.lang.block import Block

from pydash import is_empty


class Generator:
    def __init__(self, path, *, blocks: List["Block"]):
        self.path = path
        self.blocks = blocks

    def clear(self):
        if os.path.exists(self.path):
            for entry in os.listdir(self.path):
                file = os.path.join(self.path, entry)
                if os.path.isfile(file) and entry.endswith(".tf"):
                    os.remove(file)

    def create(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def write(self, block: "Block"):
        ns = block.namespace_
        if is_empty(ns):
            raise Exception("missing namespace in block")

        content = block.generate()

        with open(os.path.join(self.path, f"{ns}.tf"), "a+") as file:
            file.write(content)

    def generate(self):
        self.create()
        self.clear()

        for block in self.blocks:
            self.write(block)
