from app.transpiler.zgenerate.refactor.handlers import classcontent
from app.transpiler.zgenerate.refactor.handlers.common import self_tab
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def classcontentlist(tree, structname=None, language="py"):
    kembali = ""

    collected_content = []
    for _classcontent in anak(tree):
        hasil = classcontent.classcontent(
            _classcontent, structname=structname, language=language
        )
        if hasil:
            collected_content.append(hasil)
    if collected_content:
        # tambah ; utk item
        tabbed_class_contents = [self_tab() + item + ";" for item in collected_content]
        tabbed_class_contents = "\n".join(tabbed_class_contents)
        kembali = tabbed_class_contents

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
