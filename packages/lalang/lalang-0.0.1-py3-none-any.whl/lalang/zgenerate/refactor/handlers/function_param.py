from app.transpiler.zgenerate.refactor.handlers import paramlist
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def function_param(tree, language="py"):
    print("function_param")
    kembali = ""
    if beranak(tree):
        # paramlist
        funcparamlist = child1(tree)
        actualargs = paramlist.paramlist(funcparamlist, language=language)
        the_params = ", ".join(actualargs)
        kembali += f"({the_params})"
    else:
        kembali += f"()"

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
