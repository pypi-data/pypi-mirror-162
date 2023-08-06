# /=satu,dua,tiga/empat/
# =/satu,dua,tiga/empat/
# =/o/satu,dua,tiga/empat/
destructuring_statement = """
destructuring_statement: destructuring_markstart destructuring_config? destructuring_content destructuring_markend
destructuring_markstart: "=/"
destructuring_markend: "/"
destructuring_config: destructuringconfiglist "/"
destructuringconfiglist: destructuringconfig+
destructuringconfig: "o" -> object // default
  | "l" -> list
  | "t" -> tuple

destructuring_content: destructuring_lhs "/" destructuring_rhs
destructuring_lhs: destructuring_lhs_item ("," destructuring_lhs_item)*

destructuring_lhs_item: HURUF_DIGIT_DESTRUCTURING
destructuring_rhs: HURUF_DIGIT_DESTRUCTURING
"""
