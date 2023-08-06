literal = """
literal: literal_number
  | literal_string
  | template_string // <my name is /name/ so take care yo>
  | literal_bool
  | literal_char
  | literal_list
  | literal_dict // termasuk literal obj di sini
  | literal_tuple // termasuk pair
  | literal_pair
  | literal_set

literal_template_string: literal_string
  | template_string

literal_number: BILBUL_BERTANDA
literal_string: "\\"" HURUF_TEMPLATESTRING "\\"" // "hello"
  | "'" HURUF_TEMPLATESTRING "'" // 'hello'
template_string: "<" HURUF_TEMPLATESTRING ">"
literal_bool: "T" -> boolean_true
  | "F" -> boolean_false
literal_char: "'" LETTER "'" // 'a'

literal_list: "[" list_items* "]"
list_items: list_item ("," list_item)*
list_item: expression_item

// krn () dan {} rebutan dg func param dan body
literal_dict: "{#" dict_items* "}"
dict_items: dict_item ("," dict_item)*
dict_item: dict_item_name ":" expression_item
dict_item_name: HURUF_DIGIT

literal_tuple: "(#" tuple_items* ")"
tuple_items: tuple_item ("," tuple_item)*
tuple_item: expression_item

literal_pair: "(@" tuple_item "," tuple_item ")"

// <> skrg dipake oleh template_string
literal_set: "<#" set_items* ">"
set_items: set_item ("," set_item)*
set_item: expression_item
"""
