from app.transpiler.zgenerate.refactor.handlers import (case_body,
                                                        condition_switch)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def switch_statement(tree, language="py"):
    kembali = ""

    first_case = True
    terbanding = ""
    case_bodies = []
    for item in anak(tree):
        if data(item) == "switch_keyword":
            pass
        elif data(item) == "condition_switch":
            terbanding = condition_switch.condition_switch(item, language=language)
        elif data(item) == "case_body":
            _case_body = case_body.case_body(
                item, terbanding, first_case, language=language
            )
            case_bodies.append(_case_body)
            if first_case:
                first_case = False

    kembali += f"switch({terbanding}) {{\n"
    if case_bodies:
        case_bodies = "".join(case_bodies)
        kembali += case_bodies
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
