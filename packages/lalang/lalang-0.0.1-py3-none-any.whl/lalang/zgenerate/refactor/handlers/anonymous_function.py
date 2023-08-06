from app.transpiler.zgenerate.refactor.handlers import (anon_expression,
                                                        anon_statements,
                                                        function_config,
                                                        function_param)
from app.transpiler.zgenerate.refactor.handlers.common import (
    dec, inc, tabify_contentlist)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def anonymous_function(tree, language="py"):
    kembali = ""

    is_arrow_func_or_lambda = True  # jk hanya 1 expr
    funcconf, funcparams, funcbody = "", "", ""
    internal, external = "", ""
    for item in anak(tree):
        if data(item) == "non_arrow_func":
            is_arrow_func_or_lambda = False
        elif data(item) == "function_config":
            funcconf = function_config.function_config(item, language=language)
            funcconf = " ".join(funcconf)
        elif data(item) == "function_param":
            funcparams = function_param.function_param(item, language=language)
        elif data(item) == "anon_expression":
            hasil = anon_expression.anon_expression(item, language=language)
            internal = f"lambda item: {hasil}"
        elif data(item) == "anon_statements":
            badan_fungsi = anon_statements.anon_statements(item, language=language)
            # print('anon_statements #1:', badan_fungsi)
            if (
                len(badan_fungsi) == 1 and is_arrow_func_or_lambda
            ):  # 1 statement -> arrow
                # print('anon_statements #1a:')
                hasil = badan_fungsi[0].removesuffix(";")  # 1 expression jgn pake ;
                # print('anon_statements #2a:')
                if funcconf:
                    # print('anon_statements #3a:')
                    internal += funcconf + " "
                # print('anon_statements #4a:')
                internal += f"{funcparams} => {hasil}"
                # print('anon_statements #5a:')
            elif is_arrow_func_or_lambda:  # minta arrow -> arrow
                # print('anon_statements #1b:')
                inc()  # hrs sblm proses tabify
                funcbody = tabify_contentlist(badan_fungsi)
                dec()
                # if funcparams == '()':
                #   funcparams = '(item, index)'
                if funcconf:
                    internal += funcconf + " "
                internal += f"{funcparams} => {{\n{funcbody}\n}}"
            else:  # minta func
                # assign_name = 'anon_func'
                # internal = assign_name
                # print('anon_statements #1c:')
                inc()  # hrs sblm proses tabify
                funcbody = tabify_contentlist(badan_fungsi)
                dec()
                # if funcparams == '()':
                #   funcparams = '(item, index)'
                # external = f'def {assign_name}{funcparams}:\n' + funcbody + '\n'
                if funcconf:
                    internal += funcconf + " "
                internal += f"function {funcparams} {{\n" + funcbody + "\n}"

    # external adlh: def myanon_func(): ...
    # internal adlh: map/filter/reduce(myanon_func, mylist)
    kembali = {
        "internal": internal,
        "external": external,
    }

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
