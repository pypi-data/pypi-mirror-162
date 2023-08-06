from app.transpiler.zgenerate.refactor.handlers import (
    anonymous_function, arithmetic_expression, casting_expression,
    expression_item, function_call, literal, member_dot_expression,
    member_index_expression, range_expression, relational_expression)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def ternary_expression(tree, language="py"):
    """
    /ts/i>42?'lebih dari 42':'kurang dari samadengan 42'
    /py/i>42?'lebih dari 42':'kurang dari samadengan 42'
    """
    print("ternary_expression")
    kembali = ""
    ei_condition = child1(tree)
    ei_condition = expression_item.expression_item(ei_condition, language=language)
    ei_yes = child2(tree)
    ei_yes = expression_item.expression_item(ei_yes, language=language)
    ei_no = child3(tree)
    ei_no = expression_item.expression_item(ei_no, language=language)
    kembali = f"{ei_condition} ? {ei_yes} : {ei_no}"

    if language == "py":
        kembali = f"{ei_yes} if {ei_condition} else {ei_no}"
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
