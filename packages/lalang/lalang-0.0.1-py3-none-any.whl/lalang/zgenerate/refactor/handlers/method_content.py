from app.transpiler.zgenerate.refactor.handlers import (
    function_content, function_param, nama_identifier_with_typeparams,
    tipe_identifier)
from app.transpiler.zgenerate.refactor.handlers.common import (dec, inc,
                                                               self_tab)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def method_content(tree, language="py"):
    kembali = ""
    _tipe_identifier = ""
    for item in anak(tree):
        if data(item) == "function_name":
            _nama_identifier_with_typeparams = child1(item)
            nama = nama_identifier_with_typeparams.nama_identifier_with_typeparams(
                _nama_identifier_with_typeparams, language=language
            )
            kembali += f"{nama}"
        elif data(item) == "tipe_identifier":
            _tipe_identifier = tipe_identifier.tipe_identifier(item, language=language)
        elif data(item) == "function_param":
            kembali += function_param.function_param(item, language=language)
            # tipe fungsi stlh param
            if _tipe_identifier:
                kembali += f": {_tipe_identifier}"
        elif data(item) == "function_content":
            kembali += " {\n"
            inc()
            kembali += function_content.function_content(item, language=language)
            kembali += "\n"
            dec()
            kembali += self_tab() + "}"

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
