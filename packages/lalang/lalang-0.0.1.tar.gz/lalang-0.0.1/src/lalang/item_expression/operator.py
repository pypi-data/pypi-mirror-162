operator = """

// myobj = *MyClass{}
new_operator: "*"

arithmetic_operator: "+" -> operator_plus
  | "-" -> operator_minus
  | "*" -> operator_mult
  | "/" -> operator_float_division
  | "//" -> operator_int_floor_division
  | "%" -> operator_remainder

relational_operator: "<" -> operator_less
  | "<=" -> operator_less_equal
  | ">" -> operator_greater
  | ">=" -> operator_greater_equal
  | "==" -> operator_equal
  | "!=" -> operator_not_equal

"""
