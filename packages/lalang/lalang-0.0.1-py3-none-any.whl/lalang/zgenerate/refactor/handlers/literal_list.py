from app.transpiler.zgenerate.refactor.handlers import literal
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def literal_list(tree, language="py"):
    kembali = ""

    if not beranak(tree):
        return []
    kembalian_list = []
    list_items = child1(tree)
    # list_item = li
    for li in anak(list_items):
        ei = child1(li)
        if ei.data == "expression_item":
            item = child1(ei)
            if data(item) == "literal":
                hasil_literal = literal.literal(item, language=language)
                kembalian_list.append(hasil_literal)

    kembali = kembalian_list

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
