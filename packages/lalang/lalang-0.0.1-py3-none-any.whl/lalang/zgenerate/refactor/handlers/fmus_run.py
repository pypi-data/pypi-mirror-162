from app.fmus import Fmus
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)
from app.utils import env_int, tidur


def fmus_run(program, language="py"):
    kembali = ""
    fmus = Fmus(env_int("ULIBPY_FMUS_DEBUG"))
    # fmus.set_file_dir_template(filepath)
    # fmus.set_file_template(filepath)
    # fmus.set_dir_template_from_file(filepath)
    if env_int("ULIBPY_FMUS_CAPTURE_STDOUT_STDERR"):
        fmus.process(program, capture_outerr=True)
        if "$*" in program:
            tidur(ms=env_int("ULIBPY_STDOUT_CAPTURE_SLEEP_MS"))
            if fmus.stdout or fmus.stderr:
                kembali += fmus.stdout if fmus.stdout else fmus.stderr
    else:
        fmus.process(program)

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
