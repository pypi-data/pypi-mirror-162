from app.transpiler.zgenerate.refactor.handlers import expression_item, literal
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def for_step(tree, language="py"):
    kembali = ""

    ei = child1(tree)
    for item in anak(ei):
        if data(item) == "pre_inc_expression":
            ei2 = child1(item)
            kembali = "++" + expression_item.expression_item(ei2, language=language)
        elif data(item) == "post_inc_expression":
            ei2 = child1(item)
            kembali = expression_item.expression_item(ei2, language=language) + "++"
        elif data(item) == "pre_dec_expression":
            ei2 = child1(item)
            kembali = "--" + expression_item.expression_item(ei2, language=language)
        elif data(item) == "post_dec_expression":
            ei2 = child1(item)
            kembali = expression_item.expression_item(ei2, language=language) + "--"
        elif data(item) == "literal":
            kembali = literal.literal(item, language=language)
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
