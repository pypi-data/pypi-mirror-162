from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def function_config(tree, language="py"):
    kembali = ""

    functionconfiglist = child1(tree)
    semua_modifier = []
    for nilai in anak(functionconfiglist):
        if data(nilai) == "public":
            hasil = "public"
            semua_modifier.append(hasil)
        elif data(nilai) == "private":
            hasil = "private"
            semua_modifier.append(hasil)
        elif data(nilai) == "protected":
            hasil = "protected"
            semua_modifier.append(hasil)
        elif data(nilai) == "arrow":
            hasil = "arrow"
            semua_modifier.append(hasil)
        elif data(nilai) == "iife":
            hasil = "iife"
            semua_modifier.append(hasil)
        elif data(nilai) == "static":
            hasil = "static"
            semua_modifier.append(hasil)
        elif data(nilai) == "async":
            hasil = "async"
            semua_modifier.append(hasil)
        elif data(nilai) == "export":
            hasil = "export"
            semua_modifier.append(hasil)
        elif data(nilai) == "anonymous":
            hasil = "anonymous"
            semua_modifier.append(hasil)

    if language == "py":
        pass
    elif language == "ts":
        kembali = semua_modifier  # list
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
