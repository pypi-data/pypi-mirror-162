from app.transpiler.zgenerate.refactor.handlers import function_call_param
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def instantiation_expression(tree, language="py"):
    kembali = ""
    # hasil = ''
    for item in anak(tree):
        if data(item) == "new_operator":
            pass
        elif data(item) == "nama_identifier":
            kembali += token(item)
        elif data(item) == "function_call_param":
            hasil = function_call_param.function_call_param(item, language=language)
            kembali += hasil

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
