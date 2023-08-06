## ..5,10 = 5,6,7,8,9
## ..//5,10 = 5,6,7,8,9,10
## ../to5 = 0,1,2,3,4
## ..//to5 = 0,1,2,3,4,5
## ../from10 = 10,11,12 (default = from)
range_expression = """
range_expression: range_keyword range_expr_config? range_start "," range_stop ("," range_step)?

range_start: BILBUL
range_stop: BILBUL
range_step: BILBUL

range_expr_config: "/" range_expr_items
range_expr_items: range_expr_item ("," range_expr_item)*
// gunakan do-while, etc
range_expr_item: "/" -> range_config_close // inclusive range end, ..//start,stop,step
  | "to" -> range_config_to
  | "from" -> range_config_from
"""
