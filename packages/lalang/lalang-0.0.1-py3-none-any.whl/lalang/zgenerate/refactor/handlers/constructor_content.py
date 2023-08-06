from app.transpiler.zgenerate.refactor.handlers import (function_content,
                                                        function_param)
from app.transpiler.zgenerate.refactor.handlers.common import (dec, inc,
                                                               tabify_content)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def constructor_content(tree, structname=None, language="py"):
    kembali = ""

    ctorparam, ctorcontent = "", ""
    for item in anak(tree):
        if data(item) == "constructor_config":
            pass
        if data(item) == "function_param":
            ctorparam = function_param.function_param(item, language=language)
        if data(item) == "function_content":
            ctorcontent, jumlah_statement = function_content.function_content(
                item, language=language
            )
            if not jumlah_statement:
                ctorcontent = "{}"
            else:
                inc()
                # @my{>(){?+satu}}
                kiri = "{\n"
                kanan = "\n}"
                ctorcontent = kiri + tabify_content(ctorcontent) + kanan
                dec()

    kembali = f"{structname}{ctorparam} {ctorcontent}"
    inc()
    kembali = tabify_content(kembali)
    dec()

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
