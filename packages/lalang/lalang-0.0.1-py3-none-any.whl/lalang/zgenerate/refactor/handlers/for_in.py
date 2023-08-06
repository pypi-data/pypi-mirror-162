from app.transpiler.zgenerate.refactor.handlers import \
    nama_jenis_identifier_optional
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def for_in(tree, language="py"):
    kembali = ""

    index, items = "", ""
    for item in anak(tree):
        if data(item) == "key_name":
            _nama_jenis_identifier_optional = child1(item)
            index = nama_jenis_identifier_optional.nama_jenis_identifier_optional(
                _nama_jenis_identifier_optional, language=language
            )
        elif data(item) == "array_name":
            items = chtoken(item)
    kembali += f"(const {index} in {items})"

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
