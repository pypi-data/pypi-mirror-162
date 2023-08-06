# &myenum{yo=42, yi=43, yu=44}
enum_declaration = """
enum_declaration: enum_keyword enum_config? nama_identifier "{" enum_body "}"
enum_config: "#" -> enum_numeric // default
  | "$" -> enum_string

enum_body: enum_member_list ","?
enum_member_list: enum_member ("," enum_member)*
enum_member: nama_identifier ("=" expression_item)?
"""
