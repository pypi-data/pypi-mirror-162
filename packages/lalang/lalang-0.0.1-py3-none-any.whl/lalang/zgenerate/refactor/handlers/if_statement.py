from app.transpiler.zgenerate.refactor.handlers import (condition_then_elif,
                                                        condition_then_else,
                                                        condition_then_if)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def if_statement(tree, language="py"):
    kembali = ""

    ifpart, elsepart = "", ""
    elifparts = []
    for item in anak(tree):
        if data(item) == "if_keyword":
            pass
        elif data(item) == "condition_then_if":
            ifpart = condition_then_if.condition_then_if(item, language=language)
        elif data(item) == "condition_then_elif":
            elifpart = condition_then_elif.condition_then_elif(item, language=language)
            elifparts.append(elifpart)
        elif data(item) == "condition_then_else":
            elsepart = condition_then_else.condition_then_else(item, language=language)
    kembali += f"{ifpart}"
    if elifparts:
        elifparts = "".join(elifparts)
        kembali += elifparts
    if elsepart:
        kembali += elsepart
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
