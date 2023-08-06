from app.transpiler.zgenerate.refactor.handlers import (condition_body,
                                                        condition_for)
from app.transpiler.zgenerate.refactor.handlers.common import (dec, inc,
                                                               tabify_content)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def for_statement(tree, language="py"):
    kembali = ""

    kembali, forname, forcondition, forbody = "", "", "", ""
    for item in anak(tree):
        if data(item) == "for_keyword":
            forname = "for"
        elif data(item) == "condition_for":
            forcondition = condition_for.condition_for(item, language=language)
            # print('peroleh for condition', forcondition)
        elif data(item) == "condition_body":
            inc()
            forbody = condition_body.condition_body(item, language=language)
            if not forbody:
                forbody = "{}"
            else:
                forbody = tabify_content(forbody)
                forbody = "{\n" + forbody + "\n}"
            dec()
    # utk for traditional, hasil adlh arrayname.forEach(() => __BODY__)
    if "__BODY__" in forcondition:
        """
        for <-- forname gak perlu
        items.forEach((item, idx) => {
        __BODY__
        })
        {} <- condition_body replace __BODY__
        """
        kembali = forcondition.replace("__BODY__", forbody)
    else:
        kembali = f"{forname} {forcondition} {forbody}"

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
