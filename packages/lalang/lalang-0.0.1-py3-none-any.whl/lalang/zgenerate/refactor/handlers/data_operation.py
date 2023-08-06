from app.transpiler.zgenerate.refactor.handlers import (array_operation,
                                                        datetime_operation,
                                                        dict_operation,
                                                        file_operation,
                                                        gui_operation,
                                                        react_operation,
                                                        set_operation,
                                                        string_operation)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def data_operation(tree, identifier, language="py"):
    kembali = ""

    for item in anak(tree):
        if data(item) == "file_operation":
            kembali = file_operation.file_operation(item, language=language)
            kembali = {"type": "file_operation", "result": kembali}
        elif data(item) == "array_operation":
            kembali = array_operation.array_operation(
                item, identifier, language=language
            )
            if isinstance(kembali, dict):
                kembali["type"] = "array_operation"
        elif data(item) == "dict_operation":
            kembali = dict_operation.dict_operation(item, identifier, language=language)
            if isinstance(kembali, dict):
                kembali["type"] = "dict_operation"
        elif data(item) == "set_operation":
            kembali = set_operation.set_operation(item, identifier, language=language)
            if isinstance(kembali, dict):
                kembali["type"] = "set_operation"
        elif data(item) == "string_operation":
            kembali = string_operation.string_operation(
                item, identifier, language=language
            )
            if isinstance(kembali, dict):
                kembali["type"] = "string_operation"
        elif data(item) == "datetime_operation":
            kembali = datetime_operation.datetime_operation(
                item, identifier, language=language
            )
            if isinstance(kembali, dict):
                kembali["type"] = "datetime_operation"
        elif data(item) == "gui_operation":
            kembali = gui_operation.gui_operation(item, language=language)
            if isinstance(kembali, dict):
                kembali["type"] = "gui_operation"
        elif data(item) == "react_operation":
            kembali = react_operation.react_operation(
                item, identifier, language=language
            )
            if isinstance(kembali, dict):
                kembali["type"] = "react_operation"

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
