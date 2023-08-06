from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def range_expression(tree, language="py"):
    kembali = ""

    start, stop, step = "", "", ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "range_keyword":
            pass
        elif jenis == "range_expr_config":
            pass
        elif jenis == "range_start":
            start = token(item)
        elif jenis == "range_stop":
            stop = token(item)
        elif jenis == "range_step":
            step = token(item)
    kembali += f"{start}..{stop}"

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
