# kita pengen buka langsung fmus
# !!N
# !!N#basedir
# !!N##filename
# !!N###filepath
# !!X#...fmus code...
fmus_ops = """
fmus_ops: fmus_keyword fmus_config? fmus_cmd

fmus_config: "/" fmus_configlist "/"
fmus_configlist: fmus_configitem ("," fmus_configitem)*
fmus_configitem: "x"

fmus_cmd: fmus_new
  | fmus_execute
  | fmus_run_file

fmus_new: "N" fmus_new_args?
fmus_new_args: "#" HURUF_FOLDER -> fmus_new_basedir
  | "##" HURUF_FOLDER -> fmus_new_filename // under /tmp
  | "###" HURUF_FOLDER -> fmus_new_filepath

fmus_execute: "X#" HURUF_FMUSCODE
fmus_run_file: "R#" HURUF_DIGIT_SPASI

HURUF_FOLDER:		("_"|LETTER|DIGIT|"/"|".") 	("_"|LETTER|DIGIT|"."|"-"|"/"|","|" "|"@"|"+")*
HURUF_FMUSCODE: ("_"|LETTER|DIGIT|"*"|"/"|"."|"$"|"\\""|"("|")"|"*"|"&") (LETTER|DIGIT|"$"|"_"|"*"|"."|","|"/"|"-"|"+"|"="|"&"|"@"|"%"|"("|")"|"["|"]"|"{"|"}"|" "|":"|";"|"\\\\"|"\\""|"!"|"<"|">"|"?"|"|"|"'"|"#"|"~"|"^")*
"""
