from app.transpiler.zgenerate.refactor.handlers import expression_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def casting_expression(tree, language="py"):
    kembali = ""

    left, right = "", ""
    for item in anak(tree):
        if data(item) == "expression_item":
            if not left:
                left = expression_item.expression_item(item, language=language)
            else:
                right = expression_item.expression_item(item, language=language)

    kembali += f"{left} as {right}"

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
