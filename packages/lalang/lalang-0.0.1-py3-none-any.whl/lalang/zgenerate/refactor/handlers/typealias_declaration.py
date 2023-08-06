from app.transpiler.zgenerate.refactor.handlers import tipe_data_semua
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def typealias_declaration(tree, language="py"):
    kembali = ""

    kw, nama, nilai = "", "", ""
    for item in anak(tree):
        if data(item) == "typealias_keyword":
            kw = "type"
        elif data(item) == "nama_identifier":
            nama = token(item)
        elif data(item) == "tipe_data_semua":
            nilai = tipe_data_semua.tipe_data_semua(item, language=language)
    kembali = f"{kw} {nama} = {nilai}"

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
