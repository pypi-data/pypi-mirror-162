from app.transpiler.zgenerate.refactor.handlers import (
    anonymous_function, expression_item, named_values,
    stringify_anonymous_function_result)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def argument_list(tree, language="py"):
    kembali = ""

    args = []
    for arg in anak(tree):
        # argument
        for tipearg in anak(arg):
            if data(tipearg) == "named_values":
                # print('named_values #1')
                hasil = named_values.named_values(tipearg, language=language)
                # print('named_values #2', hasil)
                args.append(hasil)
            elif data(tipearg) == "expression_item":
                hasil = expression_item.expression_item(tipearg, language=language)
                hasil = str(hasil)
                args.append(hasil)
            elif data(tipearg) == "anonymous_function":
                hasil = anonymous_function.anonymous_function(
                    tipearg, language=language
                )
                hasil = stringify_anonymous_function_result.stringify_anonymous_function_result(
                    hasil, language=language
                )
                # kembalian AF adlh dict
                # if isinstance(hasil, dict):
                #   if 'external' in hasil and not hasil['external'] and 'internal' in hasil:
                #     hasil = hasil['internal']
                #   elif 'internal' in hasil and not hasil['internal']:
                #     hasil = hasil['external']
                args.append(hasil)

    kembali = args  # list

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
