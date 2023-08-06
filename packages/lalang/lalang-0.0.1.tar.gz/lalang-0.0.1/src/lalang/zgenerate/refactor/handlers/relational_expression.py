from app.transpiler.zgenerate.refactor.handlers import expression_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def relational_expression(tree, language="py"):
    print("relational_expression")
    kiri, kanan, oper = "", "", ""
    kembali = ""
    for item in anak(tree):
        # print('\noprek relational', type(item))
        jenis = data(item)
        if jenis == "expression_item":
            hasil = expression_item.expression_item(item, language=language)
            if not kiri:
                kiri = hasil
            else:
                kanan = hasil
        elif jenis == "operator_less":
            oper = "<"
        elif jenis == "operator_less_equal":
            oper = "<="
        elif jenis == "operator_greater":
            oper = ">"
        elif jenis == "operator_greater_equal":
            oper = ">="
        elif jenis == "operator_equal":
            oper = "=="
        elif jenis == "operator_not_equal":
            oper = "!="
    kembali = f"{kiri} {oper} {kanan}"

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
