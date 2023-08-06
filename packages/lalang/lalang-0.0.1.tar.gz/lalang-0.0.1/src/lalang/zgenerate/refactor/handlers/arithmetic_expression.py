from app.transpiler.zgenerate.refactor.handlers import (
    arithmetic_operator_to_string, expression_item)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def arithmetic_expression(tree, language="py"):
    kembali = ""

    kiri = expression_item.expression_item(child1(tree), language=language)
    oper = arithmetic_operator_to_string.arithmetic_operator_to_string(
        child2(tree), language=language
    )
    kanan = expression_item.expression_item(child3(tree), language=language)
    kembali += f"{kiri} {oper} {kanan}"

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
