from app.transpiler.zgenerate.refactor.handlers import named_value
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def named_values(tree, language="py"):
    kembali = ""

    args = []
    for nv in anak(tree):
        if data(nv) == "named_value":
            nama, jenis, nilai = named_value.named_value(nv, language=language)
            if jenis:
                args.append(f"{nama}: {jenis} = {nilai}")
            else:
                args.append(f"{nama}={nilai}")
    kembali += ", ".join(args)

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
