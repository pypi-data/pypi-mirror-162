from app.transpiler.zgenerate.refactor.handlers import expression_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def throw_statement(tree, language="py"):
    print("throw_statement")
    kembali = ""
    throwname = "Error"
    throw_expr = ""
    for item in anak(tree):
        jenis = data(item)
        # print('ketemu jenis:', jenis)
        if jenis == "throw_name":
            throwname = token(item)
        elif jenis == "expression_item":
            throw_expr = expression_item.expression_item(item, language=language)
            # print('kembali ei:', throw_expr)
    # print('nilai throw:', throw_expr)
    if language == "py":
        pass
    elif language == "ts":
        kembali += f"throw new {throwname}({throw_expr})"
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
