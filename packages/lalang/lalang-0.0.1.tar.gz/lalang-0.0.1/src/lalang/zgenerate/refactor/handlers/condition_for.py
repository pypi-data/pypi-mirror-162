from app.transpiler.zgenerate.refactor.handlers import (expression_item,
                                                        for_variation)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def condition_for(tree, language="py"):
    kembali = ""

    ei = child1(tree)
    if data(ei) == "expression_item":
        kembali += expression_item.expression_item(ei, language=language)
    elif data(ei) == "for_variation":
        kembali += for_variation.for_variation(ei, language=language)
    else:
        kembali += ""

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
