from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def function_call_config(tree, language="py"):
    kembali = ""

    functionconfiglist = child1(tree)
    semua_modifier = []
    for nilai in anak(functionconfiglist):
        if data(nilai) == "async":
            hasil = "async"
            semua_modifier.append(hasil)
        elif data(nilai) == "await":
            hasil = "await"
            semua_modifier.append(hasil)

    if semua_modifier:
        kembali = " ".join(semua_modifier)
    else:
        kembali = ""

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
