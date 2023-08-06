from app.transpiler.zgenerate.refactor.handlers import literal
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def function_call_param(tree, language="py"):
    kembali = ""
    if not beranak(tree):
        return "()"
    # callparamlist
    funcparamlist = child1(tree)
    if not beranak(funcparamlist):
        return "()"

    actualargs = []
    # print('iterate funcparamlist.children:', funcparamlist.children)
    for param in anak(funcparamlist):
        # callparam
        # print('func call param:', param)
        # nama_identifier or named_values
        if not beranak(param):
            continue
        namaid = child1(param)
        if data(namaid) == "nama_identifier":
            # print('param nama_identifier')
            argid = token(namaid)
            actualargs.append(argid)
        elif data(namaid) == "named_values":
            # print('param named_values')
            for kv in anak(namaid):
                # named_value = kv
                namaidentifier = str(kv.children[0].children[0])
                nilaiidentifier = kv.children[1]
                ei = nilaiidentifier.children[0]
                lit = ei.children[0]
                nilaiidentifierstr = literal.literal(lit, language=language)
                actualargs.append(f"{namaidentifier}={nilaiidentifierstr}")
        elif data(namaid) == "literal":
            hasil = literal.literal(namaid, language=language)
            actualargs.append(hasil)

    the_params = ", ".join(actualargs)

    kembali = f"({the_params})"

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
