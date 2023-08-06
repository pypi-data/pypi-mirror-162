from app.transpiler.zgenerate.refactor.handlers import condition_body
from app.transpiler.zgenerate.refactor.handlers.common import (dec, inc,
                                                               tabify_content)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def condition_then_else(tree, language="py"):
    kembali = ""

    ifpart, bodypart = "", ""
    for item in anak(tree):
        if data(item) == "condition_else":
            ifpart = "else"
        elif data(item) == "condition_body":
            bodypart = condition_body.condition_body(item, language=language)
            inc()
            bodypart = "{\n" + tabify_content(bodypart) + "\n}"
            dec()
    kembali += f" {ifpart} {bodypart}"

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
