from app.dirutils import here, joiner
from app.transpiler.zgenerate.refactor.handlers import (import_things,
                                                        searchable)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def import_item(tree, language="py"):
    kembali = ""
    container = None
    merged_imports = []
    search_mode = False
    hasil = ""
    filename = f"import_{language}.txt"
    for item in anak(tree):
        if data(item) == "import_container":
            container = token(item)
        elif data(item) == "import_things":
            hasil += import_things.import_things(item, language=language)
            merged_imports.append(hasil)
        elif data(item) == "searchable":
            search_mode = True
            filepath = joiner(here(__file__), "../../../data/", filename)
            print("filepath:", filepath)
            kembali += searchable.searchable(item, filepath, language=language)

    if search_mode:
        pass  # hasil sudah berisi yg diminta
    else:
        if container:
            kembali += f'import {", ".join(merged_imports)} from {container};'
        else:
            kembali += f'import {", ".join(merged_imports)};'

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
