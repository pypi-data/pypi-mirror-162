from app.transpiler.zgenerate.refactor.handlers import faker_args
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def faker_ops(tree, language="py"):
    kembali = ""

    as_list, as_string = True, False
    funcname, funcargs, callnum = "", "", 1

    # print('#1')
    for item in anak(tree):
        if data(item) == "penanda":
            pass
        elif data(item) == "faker_num":
            callnum = int(token(item))
        elif data(item) == "faker_cmd":
            funcname = token(item)
        elif data(item) == "faker_args":
            funcargs = faker_args.faker_args(item, language=language)
        elif data(item) == "as_list":
            as_list = True
        elif data(item) == "as_string":
            as_string = True
    # print('#2, args:', funcargs)
    from langs.data.fakesey import palsu

    faker = palsu.faker
    hasil = []
    # print('#3, func', funcname)
    for i in range(callnum):
        # print('\ti:', i)
        if funcargs:
            ok = getattr(faker, funcname)(*funcargs)
            # print('\t\tok:', ok)
        else:
            ok = getattr(faker, funcname)()

        if isinstance(ok, int):
            ok = str(ok)
        elif isinstance(ok, list):
            ok = str(ok)
        elif isinstance(ok, str):
            ok = '"' + ok + '"'
        # print('adding ok:', ok)
        hasil.append(ok)
    if as_string:
        kembali = ", ".join(hasil)
    elif as_list:
        kembali = "[" + ", ".join(hasil) + "]"

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
