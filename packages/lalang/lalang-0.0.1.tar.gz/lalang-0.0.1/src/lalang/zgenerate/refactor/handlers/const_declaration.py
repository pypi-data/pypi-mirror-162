from app.transpiler.zgenerate.refactor.handlers import (declaration_value,
                                                        tipe_identifier)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def const_declaration(tree, language="py"):
    kembali = ""

    nama_const, jenis_const, nilai_const = "", "", ""
    for dahan in anak(tree):
        if data(dahan) == "declaration_config":
            pass
        elif data(dahan) == "declaration_name":
            nama_const = token(dahan)
        elif data(dahan) == "tipe_identifier":
            # jenis = data(child1(dahan))
            # tipe_native = peta_tipe_data.get(jenis, jenis)
            jenis_const = tipe_identifier.tipe_identifier(dahan, language=language)
            if jenis_const:
                jenis_const = ": " + jenis_const
        elif data(dahan) == "declaration_value":
            # ei = child1(dahan)
            # nilai_variable = expression_item(ei, returning=True)
            nilai_const = declaration_value.declaration_value(dahan, language=language)

    kembali = f"const {nama_const}{jenis_const} = {nilai_const}"

    if language == "py":
        pass
    elif language == "ts":
        kembali += ";"
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
