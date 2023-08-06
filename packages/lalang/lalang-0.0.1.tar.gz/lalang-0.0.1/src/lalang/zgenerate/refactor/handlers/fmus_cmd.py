from app.dirutils import joiner, new_filename_timestamp, tempdir
from app.transpiler.editor import editor
from app.transpiler.zgenerate.refactor.handlers.fmus_run import fmus_run
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def fmus_cmd(tree, language="py"):
    kembali = ""

    code = ""
    filepath = joiner(tempdir(), new_filename_timestamp())

    for item in anak(tree):
        if data(item) == "fmus_execute":
            code = token(item)
            program = code + "\n"
            # print('executing program:', program)
            fmus_run(program, language=language)
            # print('selesai')
        elif data(item) == "fmus_new":
            for basefile in anak(item):
                if data(item) == "fmus_new_basedir":
                    basedir = token(item)
                    filepath = joiner(basedir, new_filename_timestamp())
                elif data(item) == "fmus_new_filename":
                    filename = token(item)
                    filepath = joiner(tempdir(), filename)
                elif data(item) == "fmus_new_filepath":
                    filepath = token(item)
            # pastikan filepath ada dan basedir terbuat
            program = editor(filepath)
            program = program + "\n"
            print("************")
            print(program)
            print("************")
            fmus_run(program, language=language)
    return filepath  # sementara...harusnya showtext/file utk coding

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
