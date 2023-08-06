# statement_separator = """
# statement_separator: ";"
# """

statement_list = f"""
statement_list: statement_item (statement_separator statement_item)*
"""

# condition_body: "{" single_statement* "}"

condition_body = f"""
{statement_list}

condition_body: "{{" statement_list* "}}"
"""
