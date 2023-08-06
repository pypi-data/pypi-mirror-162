from app.transpiler.zgenerate.refactor.handlers import (
    expression_item, nama_jenis_identifier_optional)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def for_start(tree, language="py"):
    kembali = ""

    keyname, range_start_value = "", ""
    for item in anak(tree):
        if data(item) == "nama_jenis_identifier_optional":
            keyname = nama_jenis_identifier_optional.nama_jenis_identifier_optional(
                item, language=language
            )
        elif data(item) == "expression_item":
            range_start_value = expression_item.expression_item(item, language=language)

    # print(f'for_start: {keyname}, {range_start_value}')
    kembali = keyname, range_start_value
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
