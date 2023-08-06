from app.transpiler.zgenerate.refactor.handlers import (condition_body,
                                                        condition_case)
from app.transpiler.zgenerate.refactor.handlers.common import (dec, inc,
                                                               self_tab,
                                                               tabify_content)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def case_body(tree, terbanding, first_case=False, language="py"):
    kembali = ""

    casehead, casebody = "", ""
    casedefault = False
    for item in anak(tree):
        # print('case body:', data(item))
        if data(item) == "condition_case":
            casehead = condition_case.condition_case(item, language=language)
        elif data(item) == "condition_defaultcase":
            casedefault = True
        elif data(item) == "condition_body":
            casebody = condition_body.condition_body(item, language=language)
            inc()
            casebody = tabify_content(casebody)
            dec()
    if casedefault:
        kembali += f"default: \n{casebody}\n"
        inc()
        kembali += f"{self_tab()}break;\n"
        dec()
    else:
        kembali += f"case {casehead}: \n{casebody}\n"
        inc()
        kembali += f"{self_tab()}break;\n"
        dec()

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
