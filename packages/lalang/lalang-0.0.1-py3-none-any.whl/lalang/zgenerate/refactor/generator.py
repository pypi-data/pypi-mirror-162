from app.transpiler.zgenerate.refactor.handlers.block_item import block_item
from app.transpiler.zgenerate.refactor.handlers.common import self_indentno
from app.transpiler.zgenerate.refactor.handlers.export_item import export_item
from app.transpiler.zgenerate.refactor.handlers.import_item import import_item
from app.transpiler.zgenerate.refactor.handlers.statement_item import \
    statement_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def do_generate(RootNode, program_context, language):
    global self_indentno
    self_indentno = 0
    kembali = ""
    if data(RootNode) == "item":
        for dahan in anak(RootNode):
            if dahan.data == "block_item":
                kembali += block_item(dahan, language=language)
            elif dahan.data == "statement_item":
                kembali += statement_item(dahan, language=language)
            elif data(dahan) == "import_item":
                kembali += import_item(dahan, language=language)
            elif data(dahan) == "export_item":
                kembali += export_item(dahan, language=language)

    elif data(RootNode) == "item_separator":
        if RootNode.children:  # jk bukan []
            newline_or_not = chdata(RootNode)
            kembali += f"\tSEP: {newline_or_not}\n"

    return kembali


def generate(RootNode, program_context={}, language="ts"):
    return do_generate(RootNode, program_context, language=language)
