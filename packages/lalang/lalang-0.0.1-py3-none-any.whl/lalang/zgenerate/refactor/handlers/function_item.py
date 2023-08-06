from app.transpiler.zgenerate.refactor.handlers import (function_config,
                                                        function_content,
                                                        function_name,
                                                        function_param,
                                                        tipe_identifier)
from app.transpiler.zgenerate.refactor.handlers.common import (dec, inc,
                                                               tabify_content)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def function_item(tree, language="py"):
    print("function_item")
    kembali = ""
    fnkw = ""
    fnconfig, fnname, fntype, fnparam, fncontent = "", "", "", "", ""
    is_anonymous = False

    for item in anak(tree):
        print("function_item anak:", data(item))
        if data(item) == "keyword_function":
            fnkw = "function"
        elif data(item) == "function_config":
            fnconfig = function_config.function_config(item, language=language)
        elif data(item) == "function_name":
            print(
                "mau panggil function name, lihat tipe:",
                type(function_name),
                type(item),
                type(language),
            )
            fnname = function_name.function_name(item, language=language)
            # kembali += 'function ' + name
        elif data(item) == "tipe_identifier":
            fntype = tipe_identifier.tipe_identifier(item, language=language)
        elif data(item) == "function_param":
            fnparam = function_param.function_param(item, language=language)
        elif data(item) == "function_content":
            inc()
            fncontent = function_content.function_content(item, language=language)
            dec()

    if language == "py":
        pass
    elif language == "ts":
        if fnconfig and "anonymous" in fnconfig:
            is_anonymous = True
            fnconfig.remove("anonymous")
        if fnconfig and "arrow" in fnconfig:
            fnconfig.remove("arrow")
            if "iife" in fnconfig:
                fnconfig.remove("iife")
                if fnconfig:
                    fnconfig = " ".join(fnconfig) + " "
                # jk iife maka gak perlu fnname dan fntype
                # (async () => {})()
                kembali += f"({fnconfig}{fnparam} => {{\n{fncontent}\n}})()"
            else:
                if fnconfig:
                    # print('#4', fnconfig, type(fnconfig))
                    kembali += " ".join(fnconfig) + " "
                if is_anonymous:
                    # (req, res) => {}
                    kembali += f"{fnparam}"
                else:
                    kembali += f"const {fnname} = {fnparam}"
                if fntype:
                    kembali += fntype
                kembali += " => {\n" + fncontent + "\n}"
        else:
            if "iife" in fnconfig:
                fnconfig.remove("iife")
                # print('#5', fnconfig, type(fnconfig))
                if fnconfig:
                    fnconfig = " ".join(fnconfig) + " "
                # jk iife maka gak perlu fnname dan fntype
                # (async () => {})()
                kembali += f"({fnconfig}function{fnparam} {{\n{fncontent}\n}})()"
            else:
                if fnconfig:
                    fnconfig = " ".join(fnconfig)
                    kembali += fnconfig + " "
                if is_anonymous:
                    # function (req, res) {}
                    kembali += f"{fnkw} {fnparam}"
                else:
                    kembali += f"{fnkw} {fnname}{fnparam}"
                if fntype:
                    kembali += fntype
                kembali += " {\n" + fncontent + "\n}"
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
