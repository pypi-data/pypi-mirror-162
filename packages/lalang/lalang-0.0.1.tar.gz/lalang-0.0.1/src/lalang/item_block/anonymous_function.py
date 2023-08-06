anonymous_function = """
// anon func digunakan di argumentlist dari func decl/def
// tidak bisa (){}
// (satu,dua)24
// (satu,dua,42){} -> hasilkan 2 model: arrowfunc dan normalfunc
// statement_item dlm condition_body dipisah oleh separator
// utk arrow func, jk hanya ada satu statement maka gak perlu {} di output
anonymous_function: non_arrow_func? function_config? function_param anonymous_function_body

// utk bilang jangan gunakan arrow func -> :
non_arrow_func: keyword_function

anonymous_function_body: "{" statement_item (statement_separator statement_item)* "}" -> anon_statements
  | expression_item -> anon_expression

"""
