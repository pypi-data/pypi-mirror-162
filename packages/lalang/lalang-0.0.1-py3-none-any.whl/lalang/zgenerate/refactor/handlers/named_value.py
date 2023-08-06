from app.transpiler.zgenerate.refactor.handlers import (expression_item,
                                                        tipe_identifier)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def named_value(tree, language="py"):
    kembali = ""

    nama, jenis, nilai = "", "", ""
    for item in anak(tree):
        if data(item) == "nama_identifier":
            nama = token(item)
        elif data(item) == "tipe_identifier":
            # jenis = chdata(item) # python gak pake type sementara
            jenis = tipe_identifier.tipe_identifier(item, language=language)
        elif data(item) == "nilai_identifier":
            ei = child1(item)
            nilai = expression_item.expression_item(ei, language=language)
    kembali = nama, jenis, nilai

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
