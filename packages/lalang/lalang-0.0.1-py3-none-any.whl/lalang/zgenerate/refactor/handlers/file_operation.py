from app.transpiler.zgenerate.refactor.handlers import expression_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def file_operation(tree, language="py"):
    kembali = ""
    for item in anak(tree):
        if data(item) == "json_out":
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali = f"JSON.stringify({hasil})"
        elif data(item) == "json_in":
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali = f"JSON.parse({hasil})"
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
