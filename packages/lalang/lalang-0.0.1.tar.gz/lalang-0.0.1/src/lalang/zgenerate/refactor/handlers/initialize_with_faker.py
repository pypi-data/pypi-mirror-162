from app.fakerutils import getfakers
from app.transpiler.zgenerate.refactor.handlers import tipe_identifier
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def initialize_with_faker(tree, language="py"):
    kembali = ""

    jumlah_data, jenis_data = "", ""
    for item in anak(tree):
        # print('oprek item bertipe:', type(item), item)
        if istoken(item):
            jumlah_data = str(item)  # jangan token(item) yg ambil children
        elif data(item) == "tipe_identifier":
            jenis_data = tipe_identifier.tipe_identifier(item, language=language)

    funcnames = {
        "string": "word",
        "int": "pyint",
        "number": "pyint",
    }
    hasil = getfakers(funcnames[jenis_data], int(jumlah_data))
    # from app.fakerutils import get_by_datatypes
    # hasil = get_by_datatypes(jenis_data, int(jumlah_data))

    kembali += hasil

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
