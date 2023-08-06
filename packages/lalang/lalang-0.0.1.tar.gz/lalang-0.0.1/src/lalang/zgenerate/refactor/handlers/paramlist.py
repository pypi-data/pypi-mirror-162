from app.transpiler.zgenerate.refactor.handlers import (nama_jenis_identifier,
                                                        named_values)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def paramlist(tree, language="py"):
    kembali = ""

    all_params = []
    for param in anak(tree):
        if not beranak(param):
            continue

        paramname_dan_tipe = ""
        paramchild = child1(param)

        if data(paramchild) == "nama_identifier":
            paramname_dan_tipe = chtoken(param)
        elif data(paramchild) == "named_values":
            paramname_dan_tipe = named_values.named_values(
                paramchild, language=language
            )
        elif data(paramchild) == "nama_jenis_identifier":
            tipe_data = nama_jenis_identifier.nama_jenis_identifier(
                paramchild, language=language
            )
            paramname_dan_tipe = tipe_data

        if paramname_dan_tipe:
            # print('param name+tipe:', paramname_dan_tipe)
            all_params.append(paramname_dan_tipe)
    kembali = all_params

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
