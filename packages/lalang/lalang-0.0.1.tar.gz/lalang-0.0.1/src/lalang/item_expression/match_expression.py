# http://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/reference/expressions/match-expr.html

# A 1 => ..., 2 => ...
# E Message::Start => ...
# I x => , &x =>
# O e @ 1..5 =>
# U 0 | 9 => ..., 1..5 =>
# * = Some(x) if x < 10 => ...

match_expression = """
match_expression: match_keyword match_patterns
"""
