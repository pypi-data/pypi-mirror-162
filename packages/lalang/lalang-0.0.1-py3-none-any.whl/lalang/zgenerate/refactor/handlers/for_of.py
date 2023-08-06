from app.transpiler.zgenerate.refactor.handlers import (
    expression_item, nama_jenis_identifier_optional)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def for_of(tree, language="py"):
    kembali = ""

    thing, things = "", ""
    for item in anak(tree):
        if data(item) == "item_name":
            _nama_jenis_identifier_optional = child1(item)
            thing = nama_jenis_identifier_optional.nama_jenis_identifier_optional(
                _nama_jenis_identifier_optional, language=language
            )
        elif data(item) == "array_name":
            for cucu in anak(item):
                if data(cucu) == "nama_identifier":
                    things = chtoken(item)
                elif data(cucu) == "expression_item":
                    things = expression_item.expression_item(cucu, language=language)
    kembali += f"(const {thing} of {things})"
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
