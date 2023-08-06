from app.transpiler.zgenerate.refactor.handlers import expression_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def destructuring_content(tree, language="py"):
    """
    destructuring_content
      destructuring_lhs
        destructuring_lhs_item      satu
        destructuring_lhs_item      dua
        destructuring_lhs_item      tiga
      destructuring_rhs     badan
    """
    kembali = ""
    kiri, kanan = "", ""
    for item in anak(tree):
        jenis = data(item)
        # print('destructuring_content:', jenis)
        if jenis == "destructuring_lhs":
            isi = [token(it) for it in anak(item)]
            kiri = ", ".join(isi)
        elif jenis == "destructuring_rhs":
            kanan = token(item)
    kembali = kiri, kanan
    return kembali


def destructuring_statement(tree, language="py"):
    """
    destructuring_statement
      destructuring_markstart
      destructuring_content
        destructuring_lhs
          destructuring_lhs_item      satu
          destructuring_lhs_item      dua
          destructuring_lhs_item      tiga
        destructuring_rhs     badan
      destructuring_markend
    """
    kembali = ""
    kiri, kanan = "", ""
    for item in anak(tree):
        jenis = data(item)
        # print('destructuring_statement:', jenis)
        if jenis == "destructuring_content":
            # print('destructuring_content', jenis)
            kiri, kanan = destructuring_content(item, language=language)

    kembali += f"const {{ {kiri} }} = {kanan}"

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
