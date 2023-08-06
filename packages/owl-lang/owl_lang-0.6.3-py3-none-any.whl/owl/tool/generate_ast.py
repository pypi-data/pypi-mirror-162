from dataclasses import dataclass
from typing import List, Tuple
import pathlib
from jinja2 import Environment, select_autoescape, FileSystemLoader

env = Environment(
    loader=FileSystemLoader(searchpath="./"), autoescape=select_autoescape()
)


@dataclass
class AstNode:
    class_name: str
    fields: List[Tuple[str, str]]
    method_class_name: str


def define_ast(base_name: str, types: List[str]):
    ast_nodes = []
    for node_type in types:
        class_name = node_type.split(":")[0].strip()
        field_str = node_type.split(":")[1].strip()
        fields: List[Tuple[str, str]] = []
        for field in field_str.split(","):
            field_type, name = field.strip().split(" ")

            fields.append((field_type, name))
        if class_name.lower().endswith("declaration"):
            method_class_name = (
                class_name.lower().replace("declaration", "") + "_" + "declaration"
            )
        else:
            method_class_name = (
                class_name.replace(base_name, "").lower() + "_" + base_name.lower()
            )

        node = AstNode(class_name, fields, method_class_name)
        ast_nodes.append(node)

    template = env.get_template(f"ast_{base_name.lower()}.template")
    ast_source = template.render(base_name=base_name, ast_nodes=ast_nodes)
    path_to = pathlib.Path("../owl_ast", f"{base_name.lower()}.py")
    path_to.write_text(ast_source, encoding="utf-8")


if __name__ == "__main__":
    print("Generate owl_ast")
    # generate statements
    define_ast(
        "Stmt",
        [
            "BlockStmt           : List[Stmt] statements",
            "ExpressionStmt      : Expr expression",
            "IfStmt              : Expr condition, Stmt then_branch, Stmt else_branch",
            "PrintStmt           : Expr expression",
            "ReturnStmt          : Token keyword, Optional[Expr] value",
            "WhileStmt           : Expr condition, Stmt body",
            "VarDeclaration      : Token name, Optional[Expr] initializer",
            "FunctionDeclaration : Token name, List[Token] parameters, List[Stmt] body",
        ],
    )
    # generate expressions
    define_ast(
        "Expr",
        [
            "Assignment      : Token name, Expr value",
            "Ternary         : Expr condition, Expr thenExpr, Expr elseExpr",
            "Logical         : Expr left, Token operator, Expr right",
            "Binary          : Expr left, Token operator, Expr right",
            "FunctionCall    : Expr callee, Token paren, List[Expr] arguments",
            "Grouping        : Expr expression",
            "Literal         : Any value",
            "Unary           : Token operator, Expr right",
            "Variable        : Token name",
        ],
    )
