from app.transpiler.zgenerate.refactor.handlers.common import (dec, inc,
                                                               tabify_content)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def create_module_and_class(ifacename, ifacecontent, language="py"):
    kembali = ""

    kembali = f"interface {ifacename} {{\n"
    inc()
    kembali += tabify_content(ifacecontent)
    dec()
    kembali += "\n}"

    kembali += "\n" * 3

    kembali += f"type {ifacename} = {{\n"
    inc()
    kembali += tabify_content(ifacecontent)
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
