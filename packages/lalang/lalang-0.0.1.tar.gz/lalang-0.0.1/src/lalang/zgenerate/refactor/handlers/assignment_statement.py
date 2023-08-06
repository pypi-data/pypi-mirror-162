from app.transpiler.zgenerate.refactor.handlers import (
    expression_item, instantiation_expression)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def assignment_statement(tree, language="py"):
    kembali = ""

    lhs, rhs = "", ""
    for item in anak(tree):
        if data(item) == "nama_identifier":
            lhs = token(item)
        elif data(item) == "instantiation_expression":
            rhs = instantiation_expression.instantiation_expression(
                item, language=language
            )
        elif data(item) == "expression_item":
            rhs = expression_item.expression_item(item, language=language)
    kembali += f"{lhs} = {rhs}"

    if language == "py":
        pass
    elif language == "ts":
        pass
    elif language == "rs":
        pass
    elif language == "java":
        pass
    elif language == "kt":
        pass
    elif language == "go":
        pass
    elif language == "rb":
        pass
    elif language == "v":
        pass
    elif language == "dart":
        pass
    elif language == "cpp":
        pass
    elif language == "cs":
        pass
    elif language == "hs":
        pass
    elif language == "clj":
        pass
    elif language == "scala":
        pass
    elif language == "php":
        pass
    elif language == "swift":
        pass
    elif language == "elixir":
        pass
    elif language == "erlang":
        pass
    return kembali
