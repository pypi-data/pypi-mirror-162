from app.transpiler.zgenerate.refactor.handlers import enum_member
from app.transpiler.zgenerate.refactor.handlers.common import self_tab
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def enum_body(tree, language="py"):
    kembali = ""

    memberlist = child1(tree)
    results = []
    for item in anak(memberlist):
        if data(item) == "enum_member":
            hasil = enum_member.enum_member(item, language=language)
            results.append(hasil)
    results = [self_tab() + item for item in results]
    kembali += ",\n".join(results)

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
