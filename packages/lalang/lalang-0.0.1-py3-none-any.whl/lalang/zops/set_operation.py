set_operation = """
set_operation:        penanda "S" set_operation_choice
// lst?A
set_operation_choice: "/" -> item_pop
  | "//"                  -> item_pop_but_stay
  | "+=" expression_item  -> concat_extend_update
  | "+" expression_item   -> insert_at_tail
  | "|"                   -> length
  | "~" expression_item   -> contains
  | "0"                   -> clear
  | "#" expression_item   -> count
  | "0?"                  -> is_empty
  | "-" expression_item   -> remove_item
  | "--" expression_item  -> remove_item_silent
  | "2s"                  -> to_string

  | "U" expression_item                  -> union
  | "X" expression_item                  -> intersection
  | "<>" expression_item                 -> difference
  | "<<>>" expression_item               -> symmetric_difference
  | "-?" expression_item                 -> is_disjoint
  | "_?" expression_item                 -> is_subset
  | "^?" expression_item                 -> is_superset

"""
