from .block import ConfigurationBlock
from ..ast.data import AstData


class Data(ConfigurationBlock):
    def generate(self) -> str:
        self.parse()

        ast = AstData(self.name_, self.type_, self.ast_())
        return ast.render()
