from app.transpiler.zgenerate.refactor.handlers import object_content
from app.transpiler.zgenerate.refactor.handlers.common import (dec, inc,
                                                               tabify_content)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def object_type(tree, language="py"):
    kembali = ""

    if not beranak(tree):
        return "{}"
    object_contents = child1(tree)
    contents = []
    for item in anak(object_contents):
        # ingat ada juga content = statement_separator
        if data(item) == "object_content":
            buah = object_content.object_content(item, language=language)
            contents.append(buah)

    kembali = "\n".join(contents)
    inc()
    kembali = tabify_content(kembali)
    dec()
    kembali = "{\n" + kembali + "\n}"

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
