switch_statement = """
switch_statement: switch_keyword switch_config? condition_switch case_body+
switch_keyword: "/s"
  | "switch"
  | "sw"
  | "s"

condition_switch: "(" expression_item ")"

case_body: (condition_case|condition_defaultcase) condition_body

condition_case: "(" expression_item ")"
condition_defaultcase: "()"

switch_config: "/" switch_config_items "/"
switch_config_items: switch_config_item ("," switch_config_item)*
// gunakan switch(literal) dll
switch_config_item: "c"
"""
