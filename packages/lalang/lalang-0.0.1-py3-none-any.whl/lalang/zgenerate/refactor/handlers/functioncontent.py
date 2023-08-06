from app.transpiler.zgenerate.refactor.handlers import statement_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def functioncontent(tree, language="py"):
    print("functioncontent")
    kembali = ""
    direct_child = child1(tree)
    if data(direct_child) == "statement_item":
        hasil = statement_item.statement_item(
            direct_child, within_statement_list=True, language=language
        )
        # print('hasil statement item:', statement_item)
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
