from app.transpiler.zgenerate.refactor.handlers import functioncontent
from app.transpiler.zgenerate.refactor.handlers.common import self_tab
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def functioncontentlist(tree, language="py"):
    print("functioncontentlist")
    kembali = ""
    allcontent = []
    for item in anak(tree):
        hasil = functioncontent.functioncontent(item, language=language)
        if hasil:
            allcontent.append(hasil)
    # print('allcontent sblm ditabify', allcontent)
    tabify = [self_tab() + item for item in allcontent]
    pemisah_content = "\n"
    kembali = pemisah_content.join(tabify)

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
