from declang.app.transpiler.frontend.bahasa import declarative_program, huruf_berbeda

from .assignment_statement import assignment_statement
from .const_declaration import const_declaration
from .declaration_config import declaration_config
from .destructuring_statement import destructuring_statement
from .typealias_declaration import typealias_declaration
from .var_declaration import var_declaration

single_statement = f"""
////////////////////////////////////////////////////////////////
// assignment
// initialization sama dg assignment?
// variable statement (dihandle $)
// typealias decl, enum decl
// throw (throw stmt), return (return stmt), yield (yield stmt), flow (continue+break stmt)
// with stmt, labelled stmt, debugger stmt
// empty stmt -> typescript hanya semicolon (terminator)
// abstract decl, namespace decl, interface decl, decorator list, generatorfunc decl
// expressionSequence adlh if(..), for(..; ..; ..), while(..), switch(..)
// tmsk di sini: function item (func+arrowfunc decl), exception item (try stmt), import item, export item, class item (class decl)
// tmsk: iteration stmt yg dihandle for+while
// tmsk: if stmt dan switch stmt yg sudah dihandle

single_statement: var_declaration
  | const_declaration
  | assignment_statement
  | flow_statement
  | return_statement
  | throw_statement
  | yield_statement
  | defer_statement
  | dataops_statement_with_identifier
  | stdout_operation
  | faker_ops
  | fmus_ops
  | redis_operation
  | typealias_declaration
  | destructuring_statement
  | "~" declarative_program

// dari go: defer statement

dataops_statement_with_identifier: nama_identifier dataops_statement

{assignment_statement}

{typealias_declaration}

flow_statement: flow_continue
  | flow_break
flow_continue: "continue"
  | "cont"
  | "co"
flow_break: "break"
  | "br"

return_statement: ">" expression_item
throw_statement: ">>" throw_name? expression_item
yield_statement: ">>>" expression_item
defer_statement: ">>>>" expression_item

throw_name: HURUF_DIGIT "/"

{destructuring_statement}

{var_declaration}

const_declaration: "%" declaration_config? declaration_name tipe_identifier? declaration_value?

{declaration_config}

declarative_program: HURUF_KODE_FRONTEND

{huruf_berbeda}
"""
