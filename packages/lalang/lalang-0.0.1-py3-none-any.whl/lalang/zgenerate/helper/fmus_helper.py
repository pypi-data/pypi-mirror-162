from app.dirutils import files, files_filter, here, joiner
from app.fileutils import file_content, file_content_add_newline
from app.fmus import Fmus
from app.greputils import pattern_search_list
from app.printutils import print_list_warna
from app.transpiler.editor import editor
from app.transpiler.zgenerate.helper.redis_helper import daftar

# pattern_search(filepath, code)
# hasil = pattern_search(filepath, terms)

# def fmus_run(self, program, capture_outerr=True):
#   fmus = Fmus(env_int('ULIBPY_FMUS_DEBUG'))
#   # fmus.set_file_dir_template(filepath)
#   # fmus.set_file_template(filepath)
#   # fmus.set_dir_template_from_file(filepath)
#   fmus.process(program, capture_outerr=capture_outerr)
#   if capture_outerr and '$*' in program:
#     tidur(ms=env_int('ULIBPY_STDOUT_CAPTURE_SLEEP_MS'))
#     if fmus.stdout or fmus.stderr:
#       self.print(fmus.stdout if fmus.stdout else fmus.stderr)

# def run_fmus_with_editor(self, filepath, initial_text='', title='New FMUS program'):
#   program = editor(filepath, initial_text=initial_text, title=title)
#   if program.strip():
#     program = program + '\n'
#     print('************')
#     print(program)
#     print('************')
#     self.fmus_run(program)


def run_fmus(sourcefile, targetfile, title="New FMUS code"):
    kodesumber = file_content_add_newline(sourcefile)
    print(f"fmus_run_file: [{kodesumber}]")
    program = editor(targetfile, initial_text=kodesumber, title=title)
    if program.strip():
        program = program + "\n"
        fmus = Fmus(True)

        fmus.set_file_dir_template(targetfile)
        if sourcefile.endswith(".mk"):
            fmus.process_mkfile(targetfile, baris_entry="program/fmus")
        elif sourcefile.endswith(".us"):
            fmus.process(program)
    else:
        print(f"\n\n*** CODE IS EMPTY ***\n\n")


fmus_dirs = joiner(here(__file__), "fmus")


def fmus_run_file(code, filepath):
    daftar_file = files_filter(fmus_dirs, [".mk", ".us"])
    program = code.strip().split()
    if code.strip() == "*":
        print_list_warna(daftar_file, genap="white", ganjil="red")
    else:
        hasil = pattern_search_list(daftar_file, program, aslist=True)
        if len(hasil) == 1:
            hasil = hasil[0]
            sourcefile = joiner(fmus_dirs, hasil)
            print(
                "fmus_run_file: ketemu nama file:",
                hasil,
                "\n->",
                sourcefile,
                "\n=>",
                filepath,
            )
            run_fmus(sourcefile, filepath)
        elif not hasil:
            print(f"\n\n*** NO RESULTS ***\n\n")
        else:
            print_list_warna(hasil, genap="white", ganjil="red")
