from app.transpiler.zgenerate.refactor.handlers import (condition_body,
                                                        condition_while)
from app.transpiler.zgenerate.refactor.handlers.common import (dec, inc,
                                                               tabify_content)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def while_statement(tree, language="py"):
    kembali = ""

    wconfig = ""
    wheader, wbody = "", ""
    for item in anak(tree):
        if data(item) == "while_keyword":
            pass
        elif data(item) == "while_config":
            pass
        elif data(item) == "condition_while":
            wheader = condition_while.condition_while(item, language=language)
        elif data(item) == "condition_body":
            wbody = condition_body.condition_body(item, language=language)
    kembali += f"while ({wheader}) {{\n"
    inc()
    kembali += tabify_content(wbody)
    dec()
    kembali += "\n}"

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
