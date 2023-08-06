while_statement = """
while_statement: while_keyword while_config? condition_while condition_body
while_keyword: "/w"
  | "while"
  | "wh"
  | "w"

condition_while: "(" expression_item ")"

while_config: "/" while_config_items
while_config_items: while_config_item ("," while_config_item)*
// gunakan do-while, etc
while_config_item: "f" -> forever_loop
"""
