float_operation = """
float_operation:        penanda "f" float_operation_choice
float_operation_choice: "h" -> hello
  | "4s" expression_item -> from_string
  | "2s" -> to_string
"""

int_operation = """
// contoh i2s, i2f
int_operation:          penanda "i" int_operation_choice
int_operation_choice: "h" -> hello
  | "4s" expression_item -> from_string // i32::from_str(val)
  | "2s" -> to_string
"""
