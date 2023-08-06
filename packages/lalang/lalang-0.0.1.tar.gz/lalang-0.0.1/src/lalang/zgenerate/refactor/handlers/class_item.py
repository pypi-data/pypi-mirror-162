from app.transpiler.zgenerate.refactor.handlers import (
    class_config, class_content, nama_identifier_with_typeparams)
from app.transpiler.zgenerate.refactor.handlers.common import dec, inc
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def class_item(tree, language="py"):
    kembali = ""

    class_modifier_start, class_modifier_end, class_name, _class_content = (
        "",
        "",
        "",
        "",
    )
    for item in anak(tree):
        if data(item) == "class_config":
            # harus cek jk interface atau interface_add maka proses class_item jadi berbeda
            class_modifier_start, class_modifier_end = class_config.class_config(
                item, language=language
            )
            # kembali += prepender + ' '
        elif data(item) == "class_name":
            # class_name
            if chdata(item) == "nama_identifier_with_typeparams":
                _nama_identifier_with_typeparams = child(item)
                class_name = (
                    nama_identifier_with_typeparams.nama_identifier_with_typeparams(
                        _nama_identifier_with_typeparams, language=language
                    )
                )
            elif chdata(item) == "nama_identifier":
                class_name = token(item)
            # kembali += f'class {namakelas} '
        elif data(item) == "class_content":
            # class_content
            inc()
            _class_content = class_content.class_content(
                item, structname=class_name, language=language
            )
            dec()

    if class_modifier_start:
        kembali += class_modifier_start + " "
    kembali += f"{class_name}"
    if class_modifier_end:
        kembali += " " + class_modifier_end
    if not _class_content:
        kembali += " {}"
    else:
        kembali += " {\n"
        kembali += _class_content
        kembali += "\n}"

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
