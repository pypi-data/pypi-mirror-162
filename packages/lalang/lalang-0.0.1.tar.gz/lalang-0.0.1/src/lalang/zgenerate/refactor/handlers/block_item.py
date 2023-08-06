from app.transpiler.zgenerate.refactor.handlers import (class_item,
                                                        function_item,
                                                        interface_item)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def block_item(tree, language="py"):
    print("block_item")
    kembali = ""
    for cucu in anak(tree):
        if cucu.data == "function_item":
            kembali += function_item.function_item(cucu, language=language)
        elif cucu.data == "class_item":
            kembali += class_item.class_item(cucu, language=language)
        elif cucu.data == "interface_item":
            kembali += interface_item.interface_item(cucu, language=language)
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
