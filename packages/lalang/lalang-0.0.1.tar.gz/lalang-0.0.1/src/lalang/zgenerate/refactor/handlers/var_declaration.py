from app.transpiler.zgenerate.refactor.handlers import (
    expression_item, instantiation_expression, tipe_identifier)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def var_declaration(tree, language="py"):
    kembali = ""
    varconfig, varname, vartype, varvalue = "", "", "", ""
    for dahan in anak(tree):
        if data(dahan) == "declaration_config":
            pass
        elif data(dahan) == "declaration_name":
            varname = token(dahan)
        elif data(dahan) == "tipe_identifier":
            vartype = tipe_identifier(dahan, language=language)
        elif data(dahan) == "declaration_value":
            ei = child1(dahan)
            if data(ei) == "expression_item":
                varvalue = expression_item(ei, language=language)
            elif data(ei) == "instantiation_expression":
                varvalue = instantiation_expression(ei, language=language)

    if language == "py":
        pass
    elif language == "ts":
        kembali += f"let {varname}"
        if vartype:
            kembali += f": {vartype}"
        if varvalue:
            kembali += f" = {varvalue}"
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
