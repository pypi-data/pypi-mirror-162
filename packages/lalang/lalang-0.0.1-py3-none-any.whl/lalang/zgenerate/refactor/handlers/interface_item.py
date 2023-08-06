from app.transpiler.zgenerate.refactor.handlers import (
    class_config, class_content, class_name, create_module_and_class)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def interface_item(tree, language="py"):
    kembali = ""

    prepender, appender = "", ""
    ifacename, ifaceconfig, ifacecontent = "", "", ""
    for item in anak(tree):
        if data(item) == "interface_keyword":
            pass
        elif data(item) == "class_name":
            ifacename = class_name.class_name(item, language=language)
        elif data(item) == "class_config":
            prepender, appender = class_config.class_config(item, language=language)
            # print('appender dan prepender utk iface:', prepender, '&', appender)
            ifaceconfig = prepender + " "
        elif data(item) == "class_content":
            ifacecontent = class_content.class_content(
                item, ifacename, language=language
            )

    # if appender:
    #   ifacename = f'{ifacename} {appender}'
    kembali = create_module_and_class.create_module_and_class(ifacename, ifacecontent)
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
