if_statement = """
// if (if) {var myvar = 24}
if_statement: if_keyword condition_then_if (condition_then_elif)* condition_then_else?

condition_then_if: condition_if condition_body
condition_then_elif: condition_elif condition_body
condition_then_else: condition_else condition_body

condition_if: "(" expression_item ")"
condition_elif: "'(" expression_item ")"
condition_else: "()"
"""
