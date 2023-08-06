from app.transpiler.zgenerate.refactor.handlers import type_parameters
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def nama_identifier_with_typeparams(tree, language="py"):
    kembali = ""
    nama_identifier = child1(tree)
    if sebanyak(tree, 2):
        _type_parameters = child2(tree)
        param_jenis = type_parameters.type_parameters(
            _type_parameters, language=language
        )
        class_namestr = token(nama_identifier) + param_jenis
    else:
        class_namestr = chtoken(tree)

    kembali = class_namestr

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
