from app.transpiler.zgenerate.refactor.handlers import (expression_item,
                                                        tipe_identifier)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def use_state(tree, identifier, language):
    kembali = ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "tipe_identifier":
            hasil = tipe_identifier.tipe_identifier(item, language)
            print("use_state => tipe_identifier:", hasil)
            # default initializer
            if hasil == "string":
                kembali = '""'
            elif hasil == "integer":  # aslinya integer
                kembali = "0"
            elif (
                hasil == "number"
            ):  # stlh /ts/ jadi number, dari peta_tipe_data dan tipe_identifier()
                kembali = "0"
            elif hasil == "boolean":
                kembali = "false"
            elif hasil == "array":
                kembali = "[]"
            elif hasil == "dict":
                kembali = "{}"
            elif hasil == "any":
                kembali = "undefined"
            elif hasil == "void":
                kembali = "null"
            else:
                kembali = hasil
        elif jenis == "state_initializer":
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language)
            print("use_state => expression_item:", hasil)
            kembali = hasil
        elif jenis == "":
            pass
    kembali += f""
    return kembali


def react_operation_cmd(tree, identifier, language="py"):
    kembali = ""
    hasil = ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "use_state":
            # print('found use_state...')
            if beranak(item):
                hasil = use_state(item, identifier, language)
                if hasil:
                    iden_lower = identifier.lower()
                    iden_set = "set" + identifier.capitalize()
                    kembali = f"const [{iden_lower}, {iden_set}] = useState({hasil})"
        elif jenis == "use_context":
            if beranak(item) and jumlahanak(item) == 2:
                # | "uc" nama_identifier "=" nama_identifier -> use_context
                kiri = chtoken(item)
                kanan = chtoken(item, 2)
                # print(kiri.pretty(), kanan.pretty())
                kembali = f"const {kiri} = useContext({kanan})"
        elif jenis == "":
            pass
    kembali += f""
    return kembali


def react_operation(tree, identifier, language="py"):
    """
    react_operation: penanda "@" react_operation_config? react_operation_cmd
    react_operation_cmd: hook_operation
      | component_operation
    """

    kembali = ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "react_operation_config":
            pass
        elif jenis == "react_operation_cmd":
            hasil = react_operation_cmd(item, identifier, language)
            kembali = hasil
        elif jenis == "":
            pass
    kembali += f""
    return kembali
