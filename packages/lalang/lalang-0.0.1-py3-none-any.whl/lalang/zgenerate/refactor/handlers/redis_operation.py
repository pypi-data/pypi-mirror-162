from app.printutils import print_enumerate
from app.transpiler.zgenerate.helper.redis_helper import redis_process
from app.transpiler.zgenerate.refactor.handlers import redis_args
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def redis_operation(tree, language="py"):
    kembali = ""

    cmd, thing = "", ""
    args = []
    for item in anak(tree):
        if data(item) == "penanda":
            pass
        elif data(item) == "redis_string_get":
            cmd = "get"
        elif data(item) == "redis_string_add":
            cmd = "set"
        elif data(item) == "redis_keys":
            cmd = "list"
        elif data(item) == "redis_key":
            thing = token(item)
            args.append(thing)
        elif data(item) == "redis_value":
            thing = token(item)
            args.append(thing)
        elif data(item) == "redis_args":
            args = redis_args.redis_args(item, language=language)

    hasil = redis_process(cmd, args)
    print(f"redis_process({cmd}, {args})", hasil)
    if isinstance(hasil, list):
        hasil = [item.decode("utf8") for item in hasil]
        print_enumerate(hasil)
        kembali = "\n".join(hasil)
    elif isinstance(hasil, str):
        kembali = hasil
    elif isinstance(hasil, bytes):
        kembali = hasil.decode("utf8")
    else:
        print("result:", type(hasil))

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
