from app.transpiler.zgenerate.refactor.handlers import expression_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def dict_operation(tree, identifier, language="py"):
    kembali = ""

    for item in anak(tree):
        if data(item) == "penanda":
            pass
        elif data(item) == "concat_extend_update":
            """
            "+=" expression_item
            concat_extend_update
              expression_item
                literal
                  literal_dict
                    dict_items
                      dict_item
                        dict_item_name        a
                        expression_item
                          literal
                            literal_number    1
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.update({hasil})"
        elif data(item) == "get_item":
            """
            "/" literal ("/" literal)?
            iden.get(item, item)
            get_item
              expression_item
                nama_identifier       item
              expression_item
                nama_identifier       default
            """
            ei = child1(item)
            hasil1 = expression_item.expression_item(ei, language=language)
            hasil2 = hasil1
            if jumlahanak(item) == 2:
                ei2 = child2(item)
                hasil2 = expression_item.expression_item(ei2, language=language)
            kembali += f"{identifier}.get({hasil1}, {hasil2})"
        elif data(item) == "length":
            """
            dik?D|
            """
            kembali += f"Object.keys({identifier}).length"
        elif data(item) == "assign":
            """
            "+" expression_item "=" expression_item
            dik[item]=nilai
            dik?D+item=nilai
            """
            ei1 = child1(item)
            ei2 = child2(item)
            hasil1 = expression_item.expression_item(ei1, language=language)
            hasil2 = expression_item.expression_item(ei2, language=language)
            kembali += f"{identifier}[{hasil1}] = {hasil2}"
        elif data(item) == "has_item":
            """
            "~(" expression_item ")"
            """
            ei1 = child1(item)
            hasil1 = expression_item.expression_item(ei1, language=language)
            kembali += f"{hasil1} in {identifier}.values()"
        elif data(item) == "remove_item":
            """
            "-(" expression_item ")"
            filtereddik = {k:v for k,v in identifier.items() if v != hasil}
            """
            ei1 = child1(item)
            hasil1 = expression_item.expression_item(ei1, language=language)
            kembali += f"{{k:v for k,v in {identifier}.items() if v != {hasil1}}}"
        elif data(item) == "has_key":
            """
            "~" expression_item
            """
            ei1 = child1(item)
            hasil1 = expression_item.expression_item(ei1, language=language)
            # kembali += f'{hasil1} in {identifier}'
            kembali += f"{identifier}.includes({hasil1})"
        elif data(item) == "remove_key":
            """
            "-" expression_item
            """
            ei1 = child1(item)
            hasil1 = expression_item.expression_item(ei1, language=language)
            kembali += f"del {identifier}[{hasil1}]"
        elif data(item) == "clear":
            """
            dik?D0
            """
            kembali += f"{identifier}.clear()"
        elif data(item) == "remove_at_tail":
            """
            popitem = remove last inserted
            dik?D->
            """
            kembali += f"{identifier}.popitem()"
        elif data(item) == "remove_at_index":
            """
            dik?D-@5
            """
            hasil = token(item)
            kembali += f"{identifier}.pop({hasil})"
        elif data(item) == "is_empty":
            """
            dik?D0?
            """
            # kembali += f'len({identifier}) == 0'
            kembali += identifier
        elif data(item) == "entries":
            """
            dik?D@
            """
            kembali += f"{identifier}.entries()"
        elif data(item) == "keys":
            """
            dik?D#
            """
            kembali += f"{identifier}.keys()"
        elif data(item) == "values":
            """
            dik?D$
            """
            kembali += f"{identifier}.values()"
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
