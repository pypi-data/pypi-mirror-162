from app.transpiler.zgenerate.refactor.handlers import expression_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def stdout_operation(tree, language="py"):
    kembali = ""
    nilai = ""
    for item in anak(tree):
        # kita iterate utk antisipasi masa depan mau tambah child = config etc
        # misa utk print logger, DebugOutputString dst.
        if data(item) == "console_log":
            ei = child1(item)
            nilai = expression_item.expression_item(ei, language=language)

    if language == "py":
        pass
    elif language == "ts":
        kembali += f"console.log({nilai})"
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
        kembali += f"Console.WriteLine({nilai})"
    elif language == "hs":
        kembali += f"putStrLn {nilai}"
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
