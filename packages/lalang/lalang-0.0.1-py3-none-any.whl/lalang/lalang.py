import datetime
# import os, sys
# import lark, json, os, pyperclip, subprocess, sys
from lark import InlineTransformer, Lark

# from langutils.app.dirutils import (ayah, joiner, here)
from langutils.app.printutils import indah3, print_json
from langutils.app.utils import trycopy
from .config import daftar_languages, program_context
from .grammar import bahasa

from .zgenerate.helper.redis_helper import ada_inlist, getstr


class TheProcessor(InlineTransformer):
    def program(self, *item_lines):
        return item_lines


def process_program_configuration_items(childrens):
    for item in childrens:
        if item.data == "program_configuration_item":
            lang_lib_frame_tool_ctx = item.children[0]
            lang_config = lang_lib_frame_tool_ctx.data
            if lang_config in daftar_languages:
                if lang_config not in program_context["language_context"]:
                    program_context["language_context"].append(lang_config)
            elif lang_config == "library_context":
                """
                library_context
                        library_items
                                library_item    mylib
                """
                items = lang_lib_frame_tool_ctx.children[0]
                for item in items.children:
                    itemname = str(item.children[0])
                    if itemname not in program_context["library_context"]:
                        program_context["library_context"].append(itemname)
            elif lang_config == "framework_context":
                """
                framework_context
                        framework_items
                                framework_item  myframework
                """
                items = lang_lib_frame_tool_ctx.children[0]
                for item in items.children:
                    itemname = str(item.children[0])
                    if itemname not in program_context["framework_context"]:
                        program_context["framework_context"].append(itemname)
            elif lang_config == "tools_context":
                """
                tools_context
                        tools_items
                                tools_item      mytools
                """
                items = lang_lib_frame_tool_ctx.children[0]
                for item in items.children:
                    itemname = str(item.children[0])
                    if itemname not in program_context["tools_context"]:
                        program_context["tools_context"].append(itemname)


def process_language(code, returning=False, print_header_for_result=False):
    global program_context
    parser = Lark(bahasa, start="program").parse
    print("=" * 20, code, "\n")
    parsed_tree = parser(code)
    instructions = TheProcessor().transform(parsed_tree)

    hasil_dalam_list = []
    bahasa_terpilih = []
    # daftar = list(daftar_languages.keys())
    # daftar = ['python']
    # daftar = ['python', 'typescript', 'dart', 'golang', 'rust', 'kotlin', 'java', 'ruby']
    daftar = ["py", "ts", "dart", "go", "rs", "kt", "java", "rb"]
    if ada_inlist("ulangsingle", daftar_languages.keys()):
        daftar = [getstr("ulangsingle")]
    # print('daftar =', daftar)

    for insn in instructions:  # instructions adlh tuple
        # insn = program_language, item_line
        for tree in insn.children:  # insn adlh Tree
            print(tree.pretty())
            if tree.data == "program_configuration_items":
                """
                set
                        program_context['language_context']
                among other things
                """
                process_program_configuration_items(tree.children)
                if (
                    program_context
                    and "language_context" in program_context
                    and program_context["language_context"]
                ):
                    daftar = program_context["language_context"]
                    print("program_configuration_items => chosen languages =", daftar)

            elif tree.data in ["item", "item_separator"]:
                # print('oprek tree', tree)
                for lang in daftar:
                    # panggil generate dari gen_*.py
                    hasil = daftar_languages[lang](tree, program_context)
                    if hasil:
                        hasil_dalam_list.append(hasil)
                        bahasa_terpilih.append(lang)
                    # else:
                    # 	# hasil item_separator diskip
                    # 	# tapi nantinya dipake, utk bisa programmatically create newline etc
                    # 	# print(f'skipping [{lang}]')
                    # 	pass

    # print_json(program_context)

    # kosongkan setiap kali invoke, biar gak numpuk
    program_context = {
        "language_context": [],
        "library_context": [],
        "framework_context": [],
        "tools_context": [],
    }

    if print_header_for_result:
        dipisah = [
            ("//" + f" {bahasa_terpilih[idx]}\n") + item
            for (idx, item) in enumerate(hasil_dalam_list)
        ]
    else:
        dipisah = hasil_dalam_list

    if returning:
        # masih versi list
        return dipisah

    dipisah = "\n".join(dipisah)
    indah3(dipisah, warna="white")


shortcuts = {
    "`i": "py/?K5/pyint",  # list of 5 ints
    "`rl": "py/?r=*",  # redis list
}


snippets_key = "__"


def process_language_wrapper(code):

    # handle shortcuts
    if code.startswith(snippets_key):
        program = code.removeprefix(snippets_key).strip()
        from .snippets import cari_asstring

        hasil = cari_asstring(program)
        return hasil

    if [item for item in shortcuts.keys() if code.startswith(item)]:
        kunci = [item for item in shortcuts.keys() if code.startswith(item)][0]
        nilai = shortcuts[kunci]
        # `i(10,15) -> /py/?K5/pyint(10,15)
        # perlu bisa ganti K5 menjadi args spt `i(10,15)#10 utk jadi 10 items
        code = code.replace(kunci, nilai)

    return process_language(code, returning=True, print_header_for_result=False)


def myrepl():
    code = 1
    while code != "x":
        try:
            code = input(
                f'{datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")} >> '
            )
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


def quick_repl():
    code = 1
    while code != "x":
        try:
            # prompt = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            prompt = datetime.datetime.utcnow().isoformat()
            code = input(f"LALANG {prompt} >> ")
            code = code.strip()
            if code == "bahasa":
                indah3(bahasa, warna="green")
            elif code != "" and code != "x":
                process_language(code)
        except EOFError as eof:
            print("Ctrl+D? Exiting...", eof)
            break
        except Exception as err:
            print(err)


if __name__ == "__main__":
    myrepl()
