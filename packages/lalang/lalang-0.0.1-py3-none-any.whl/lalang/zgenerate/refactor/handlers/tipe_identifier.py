from app.transpiler.zgenerate.refactor.handlers.common import peta_tipe_data
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def handle_array(tree, language="py"):
    kembali = "[]"
    kembali += f""
    return kembali


def handle_dict(item, language="py"):
    kembali = ""
    keytype, valtype = "", ""

    if jumlahanak(item) == 2:
        keytype = child(item, 1)
        keytype = chdata(keytype)
        valtype = child(item, 2)  # value_type
        valtype = chdata(valtype)  # string
    if language == "py":
        kembali = "{}"
    elif language == "ts":
        # https://stackoverflow.com/questions/15877362/declare-and-initialize-a-dictionary-in-typescript
        # https://www.carlrippon.com/typescript-dictionary/
        if keytype and valtype:
            kunci = peta_tipe_data[language].get(keytype, keytype)
            nilai = peta_tipe_data[language].get(valtype, valtype)
            kembali = f"new Record<{kunci}, {nilai}>()"
        else:
            kembali = f"new Record()"
    elif language == "js":
        # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map
        # let scores = new Map<string, number>();
        if keytype and valtype:
            kunci = peta_tipe_data[language].get(keytype, keytype)
            nilai = peta_tipe_data[language].get(valtype, valtype)
            kembali = f"new Map<{kunci}, {nilai}>()"
        else:
            kembali = f"new Map()"
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
        # if beranak(item) and sebanyak(item, 2):
        """
        | "D" (key_type "," value_type)?    -> dict
        dict
          key_type
            integer
          value_type
            string
        """
        if keytype and valtype:
            kunci = peta_tipe_data[language].get(keytype, keytype)
            nilai = peta_tipe_data[language].get(valtype, valtype)
            kembali = f"Map<{kunci}, {nilai}>"
        else:
            kembali = f"Map<?, ?>"
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
    kembali += f""
    return kembali


def handle_set(tree, language="py"):
    kembali = "set()"
    kembali += f""
    return kembali


def handle_tuple(tree, language="py"):
    kembali = "()"
    kembali += f""
    return kembali


def handle_pair(tree, language="py"):
    kembali = "()"
    kembali += f""
    return kembali


def tipe_identifier(tree, language="py"):
    kembali = ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "tipe_data_buatan":
            kembali = chtoken(item)
        elif jenis in ["array", "dict", "pair", "set", "tuple"]:
            if jenis == "array":
                if beranak(item) and chdata(item) == "item_type":
                    tipeanak = chdata(child(item))  # item=array / item_type / string
                    kembali = peta_tipe_data[language].get(tipeanak, tipeanak) + "[]"
                else:
                    kembali = "[]"
            elif jenis == "set":
                if beranak(item) and chdata(item) == "item_type":
                    tipeanak = chdata(child(item))  # item=array / item_type / string
                    kembali = f"Set<{peta_tipe_data.get(tipeanak, tipeanak)}>"
                else:
                    kembali = "Set<?>"
            elif jenis == "dict":
                kembali = handle_dict(item, language)
            elif jenis == "pair":
                if beranak(item) and sebanyak(item, 2):
                    """ """
                    keytype = child(item, 1)
                    keytype = chdata(keytype)
                    valtype = child(item, 2)  # value_type
                    valtype = chdata(valtype)  # string
                    kunci = peta_tipe_data.get(keytype, keytype)
                    nilai = peta_tipe_data.get(valtype, valtype)
                    kembali = f"Pair<{kunci}, {nilai}>"
                else:
                    kembali = f"Pair<?, ?>"
        else:
            jenis = data(item)
            kembali = peta_tipe_data[language].get(jenis, jenis)

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
