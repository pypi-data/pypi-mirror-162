from .block import AbstractBlock
from .decorators import schema
from ..ast.terraform import AstTerraform


@schema
class Terraform(AbstractBlock):
    @property
    def namespace_(self):
        return "main"

    def generate(self) -> str:
        self.parse()

        ast = AstTerraform(self.ast_())
        return ast.render()
