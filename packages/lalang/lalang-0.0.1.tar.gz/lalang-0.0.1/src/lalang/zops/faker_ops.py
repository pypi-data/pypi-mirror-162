# 10/random_int
# 10/random_int(0,100)
# 10/random_int(0,100)/A
faker_ops = """
faker_ops: penanda "K" faker_num "/" faker_cmd faker_args? as_output?
faker_num: BILBUL
faker_cmd: HURUF_DIGIT // nama fungsi
faker_args: "(" fake_arg ("," fake_arg)* ")"
fake_arg: HURUF_FUNCTIONCALL_ARGS
// default as_string utk 1 num, as_list utk multiple num
as_output: "/A" -> as_list
  | "/D" -> as_dict
  | "/S" -> as_set
  | "/L" -> as_tuple
  | "/P" -> as_pair
  | "/s" -> as_string
  | "/i" -> as_int

//HURUF_DIGIT: 						("_"|LETTER|DIGIT) 	("_"|LETTER|DIGIT|".")*
// ' hrs bisa mendahului spt 'int', 'str', utk literal string
// juga [] utk literal list
HURUF_FUNCTIONCALL_ARGS:   ("_"|LETTER|DIGIT|"'"|"["|"]") 	("_"|LETTER|DIGIT|" "|"."|"-"|"+"|"/"|"@"|"'"|"["|"]")*
"""
