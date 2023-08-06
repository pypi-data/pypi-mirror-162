from app.transpiler.zgenerate.refactor.handlers import \
    nama_identifier_with_typeparams
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def function_name(tree, language="py"):
    print("function_name")
    kembali = ""
    _nama_identifier_with_typeparams = child1(tree)
    name = nama_identifier_with_typeparams.nama_identifier_with_typeparams(
        _nama_identifier_with_typeparams, language=language
    )

    if language == "py":
        pass
    elif language == "ts":
        kembali = name
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
