from app.transpiler.zgenerate.refactor.handlers import classcontentlist
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def class_content(tree, structname=None, language="py"):
    kembali = ""

    _classcontentlist = child1(tree)
    if beranak(_classcontentlist):
        hasil = classcontentlist.classcontentlist(
            _classcontentlist, structname=structname, language=language
        )
        kembali += hasil
    else:
        kembali += "{}"

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
