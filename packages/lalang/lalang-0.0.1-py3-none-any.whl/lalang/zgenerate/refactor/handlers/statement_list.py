from app.transpiler.zgenerate.refactor.handlers import statement_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def statement_list(tree, language="py"):
    kembali = ""

    statements = []
    for stmt in anak(tree):
        if data(stmt) == "statement_item":
            output = statement_item.statement_item(
                stmt, within_statement_list=True, language=language
            )
            if not output.endswith(";"):
                output += ";"
            statements.append(output)
        elif data(stmt) == "statement_separator":
            pass

    if statements:
        statements = "\n".join(statements)
        kembali += statements

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
