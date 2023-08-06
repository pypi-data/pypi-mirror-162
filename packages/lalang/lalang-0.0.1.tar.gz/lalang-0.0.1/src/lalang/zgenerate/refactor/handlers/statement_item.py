from app.transpiler.zgenerate.refactor.handlers import (
    enum_declaration, expression_item, for_statement, if_statement,
    instantiation_expression, single_statement, switch_statement,
    while_statement)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def statement_item(tree, within_statement_list=False, language="py"):
    print("statement_item")
    kembali = ""
    statement = child1(tree)
    if data(statement) == "single_statement":
        kembali += single_statement.single_statement(statement, language=language)
    elif data(statement) == "instantiation_expression":
        kembali += instantiation_expression.instantiation_expression(
            statement, language=language
        )
    elif data(statement) == "for_statement":
        kembali += for_statement.for_statement(statement, language=language)
    elif data(statement) == "if_statement":
        kembali += if_statement.if_statement(statement, language=language)
    elif data(statement) == "expression_item":
        kembali += expression_item.expression_item(statement, language=language)
    elif data(statement) == "while_statement":
        kembali += while_statement.while_statement(statement, language=language)
    elif data(statement) == "switch_statement":
        kembali += switch_statement.switch_statement(statement, language=language)
    elif data(statement) == "enum_declaration":
        kembali += enum_declaration.enum_declaration(statement, language=language)

    if language == "py":
        pass
    elif language == "ts":
        # if not kembali.endswith(';') and not within_statement_list:
        if not kembali.endswith(";"):
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
