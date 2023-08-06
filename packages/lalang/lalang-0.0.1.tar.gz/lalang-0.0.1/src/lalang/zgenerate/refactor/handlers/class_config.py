from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def class_config(tree, language="py"):
    kembali = ""

    classconfiglist = child1(tree)
    semua_modifier = []
    prepender, appender = "", ""
    for nilai in anak(classconfiglist):
        # print('oprek nilai:', nilai)
        if data(nilai) == "public":
            hasil = "public"
            semua_modifier.append(hasil)
        elif data(nilai) == "private":
            hasil = "private"
            semua_modifier.append(hasil)
        elif data(nilai) == "protected":
            hasil = "protected"
            semua_modifier.append(hasil)
        elif data(nilai) == "static":
            hasil = "static"
            semua_modifier.append(hasil)
        elif data(nilai) == "abstract":
            hasil = "abstract"
            semua_modifier.append(hasil)
        elif data(nilai) == "async":
            hasil = "async"
            semua_modifier.append(hasil)
        elif data(nilai) == "extends":
            """
            extends
              nama_identifier     Sports
            """
            appender = "extends " + chtoken(nilai)

    if semua_modifier:
        prepender = " ".join(semua_modifier)

    kembali = prepender, appender

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
