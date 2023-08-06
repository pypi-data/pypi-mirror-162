import datetime
from langutils.app.utils import trycopy
from . import process_language
from .lalang import shortcuts, bahasa



def myrepl():
    code = 1
    while code != "x":
        try:
            code = input(f'LALANG {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")} >> ')
            code = code.strip()
            if code == "bahasa":
                print(bahasa)
                trycopy(bahasa)
            elif [item for item in shortcuts.keys() if item.startswith(code)]:
                # sementara blm pake args
                program = shortcuts[code]
                print(f"convert code from {code} to {program}")
                process_language(program)
            elif code != "" and code != "x":
                process_language(code)
        except EOFError as eof:
            print("Ctrl+D? Exiting...", eof)
            break
        except Exception as err:
            print(err)

if __name__ == "__main__":
    myrepl()
