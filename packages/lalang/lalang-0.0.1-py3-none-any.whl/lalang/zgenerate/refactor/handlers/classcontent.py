from app.transpiler.zgenerate.refactor.handlers import (constructor_content,
                                                        field_content,
                                                        method_content)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def classcontent(tree, structname=None, language="py"):
    kembali = ""

    if not beranak(tree):
        return None

    ctor_method_field = child1(tree)
    if ctor_method_field.data == "constructor_content":
        item = constructor_content.constructor_content(
            ctor_method_field, structname=structname, language=language
        )
        # collected_content.append(item)
        kembali = item
    elif data(ctor_method_field) == "method_content":
        item = method_content.method_content(ctor_method_field, language=language)
        kembali = item
    elif data(ctor_method_field) == "field_content":
        item = field_content.field_content(ctor_method_field, language=language)
        kembali = item

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
