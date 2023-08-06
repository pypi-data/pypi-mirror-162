from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def redis_args(tree, language="py"):
    kembali = ""

    redis_arg = child1(tree)
    # kembali = ''
    args = []
    for item in anak(redis_arg):
        if data(item) == "redis_key":
            hasil = token(item)
            args.append(hasil)
        elif data(item) == "redis_value":
            # sementara value masih string
            # nanti bisa: dict, list, set
            hasil = token(item)
            args.append(hasil)

    kembali = args

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
