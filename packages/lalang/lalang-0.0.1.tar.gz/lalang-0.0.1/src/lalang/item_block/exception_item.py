exception_item = """
exception_item: exception_keyword exception_config? try_content except_content finally_content?

exception_config: "/" exceptionconfiglist "/"
exceptionconfiglist: exceptionconfig ("," exceptionconfig)*
// mungkin bisa kasih nama utk exception?
exceptionconfig: "x"

try_content: condition_body

//trycontentlist: trycontent ("," trycontent)*
//trycontent: "t"
//  | statement_item
//  |

except_content: exceptcontentlist
exceptcontentlist: exceptcontent (exceptcontent)*
exceptcontent: on_block_version? "(" exception_header ")" condition_body
exception_header: HURUF_DIGIT
on_block_version: "*" -> on_block
  | "$" -> on_catch_block // on IntegerDivisionByZeroException catch(e)

//except_content: "(" exceptcontentlist ")"
//exceptcontentlist: exceptcontent ("," exceptcontent)*
//exceptcontent: "x"
//  | statement_item
//  |

finally_content: "()" condition_body

//finally_content: "(" finallycontentlist ")"
//finallycontentlist: finallycontent ("," finallycontent)*
//finallycontent: "f"
//  | statement_item
//  |
"""
