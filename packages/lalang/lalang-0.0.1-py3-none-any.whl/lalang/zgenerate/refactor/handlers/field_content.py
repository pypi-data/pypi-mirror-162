from app.transpiler.zgenerate.refactor.handlers import (declaration_value,
                                                        tipe_identifier)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def field_content(tree, language="py"):
    kembali = ""

    fieldconfig, fieldname, fieldtype, fieldvalue = "", "", "", ""
    for item in anak(tree):
        if data(item) == "field_config":
            pass
        elif data(item) == "field_name":
            fieldname = token(item)
            # print('\t nama =', fieldname)
        elif data(item) == "tipe_identifier":
            fieldtype = tipe_identifier.tipe_identifier(item, language=language)
            # print('\t jenis =', fieldtype)
        elif data(item) == "declaration_value":
            fieldvalue = declaration_value.declaration_value(item, language=language)
            # print('\t nilai =', fieldvalue)
    if fieldconfig:
        kembali += fieldconfig + " "
    kembali += fieldname
    if fieldtype:
        kembali += f": {fieldtype}"
    if fieldvalue:
        kembali += " = " + fieldvalue

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
