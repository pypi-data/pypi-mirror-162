from app.transpiler.zgenerate.refactor.handlers import statement_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def anon_statements(tree, language="py"):
    kembali = ""

    statement_list = []
    for statement in anak(tree):
        if data(statement) == "statement_item":
            # skip statement_separator
            hasil = statement_item.statement_item(
                statement, within_statement_list=True, language=language
            )
            print("hasil dari statement item dalam anonstats:", hasil)
            hasil = str(hasil)  # si -> ei -> suka hasilkan number
            statement_list.append(hasil)

    # print('peroleh statement_list:', statement_list)
    # list
    kembali = statement_list

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
