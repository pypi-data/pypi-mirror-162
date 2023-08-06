# :xwi/myfunc:i(){}
function_item_header = """
function_item: keyword_function function_config? function_name tipe_identifier? function_param function_content

function_config: functionconfiglist "/"

//functionconfiglist: functionconfig ("," functionconfig)*
//:ai/foo(){}
functionconfiglist: functionconfig+

// language config -> /js, /py, /kt, /rs, /scala
// decorator
// async
// iife
// anonymous, lambda, closure, inner, arrow
// contoh di rust: const myconst = async (funcparams): Promise<sometype> => {}
// export + default
functionconfig: "+" -> public
  | "-" -> private
  | "#" -> protected
  | "%" -> static
  | "a" -> async
  | "x" -> export
  | "w" -> arrow
  | "i" -> iife
  | "no" -> anonymous

function_name: nama_identifier_with_typeparams

function_type: ":" HURUF_DIGIT

function_param: "(" paramlist* ")"
paramlist: param ("," param)*
// nama_jenis_identifier_optional = nama_identifier | nama_jenis_identifier
param: named_values
  | nama_identifier
  | nama_jenis_identifier
  | nama_jenis_identifier_nullable

// digunakan di expression-item:
// new_operator nama_identifier function_call_param -> instantiation_expression
function_call_param: "(" callparamlist* ")"
callparamlist: callparam ("," callparam)*
callparam: named_values
  | nama_identifier
  | literal  

// ini jadi setara dg function_call_param
argument_list: argument ("," argument)*
argument: expression_item
  | named_values
  | anonymous_function

function_content: "{" functioncontentlist* "}"
functioncontentlist: functioncontent (statement_separator functioncontent)*
functioncontent: statement_item
"""

from .anonymous_function import anonymous_function

function_item = f"""
{function_item_header}

{anonymous_function}
"""
