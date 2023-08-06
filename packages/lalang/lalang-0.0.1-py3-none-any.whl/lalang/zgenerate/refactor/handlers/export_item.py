from app.transpiler.zgenerate.refactor.handlers import (export_config,
                                                        export_content)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def export_item(tree, language="py"):
    kembali = ""
    xkw = ""
    xconf, xcontents = "", ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "keyword_export":
            xkw = "export"
        elif jenis == "export_config":
            xconf = export_config.export_config(item, language=language)
        elif jenis == "export_content":
            xcontents = export_content.export_content(item, language=language)
    kembali += xkw + " "
    if xconf:
        kembali += f"{xconf} "
    kembali += xcontents

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
