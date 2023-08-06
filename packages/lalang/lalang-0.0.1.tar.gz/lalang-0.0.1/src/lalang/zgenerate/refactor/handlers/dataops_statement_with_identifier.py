from app.transpiler.zgenerate.refactor.handlers import dataops_statement
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def dataops_statement_with_identifier(tree, language="py"):
    kembali = ""

    identifier, rhs = "", ""
    for item in anak(tree):
        if data(item) == "nama_identifier":
            identifier = token(item)
        elif data(item) == "dataops_statement":
            rhs = dataops_statement.dataops_statement(
                item, identifier, language=language
            )

    if language == "py":
        if isinstance(rhs, dict):
            """
            kembalian anon func: dict berisi internal dan external
            """
            if rhs["type"] == "array_operation":
                operasi = rhs["operation"]
                if rhs["external"]:
                    kembali += f"{rhs['external']}\n"
                    kembali += "{operasi}({rhs['internal']}, {identifier})"
                else:
                    kembali = f"{operasi}({rhs['internal']}, {identifier})"
            elif rhs["type"] == "file_operation":
                kembali = f'const {identifier} = {rhs["result"]}'
        elif isinstance(rhs, str):
            kembali = rhs
    elif language == "ts":
        if isinstance(rhs, dict):
            """
            kembalian anon func: dict berisi internal dan external
            """
            if rhs["type"] == "array_operation":
                operasi = rhs["operation"]
                if rhs["external"]:
                    kembali += f"{rhs['external']}\n"
                    kembali += f"{identifier}.{operasi}({rhs['internal']})"
                else:
                    kembali = f"{identifier}.{operasi}({rhs['internal']})"
            elif rhs["type"] == "file_operation":
                kembali = f'const {identifier} = {rhs["result"]}'
        elif isinstance(rhs, str):
            kembali = rhs
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
