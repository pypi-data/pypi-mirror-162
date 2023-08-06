expression_item_header = """
expression_item: function_call  // myfunc(34), myfunc(param1=42)
  | anonymous_function          // (req,res){}
  | literal
  | member_dot_expression
  | member_index_expression
  | casting_expression
  | expression_with_operator
  | nama_identifier
  | new_operator nama_identifier function_call_param -> instantiation_expression
  | range_expression

casting_expression: expression_item (keyword_casting expression_item)+

expression_with_operator: "!" expression_item -> not_expression
  | "++" expression_item -> pre_inc_expression
  | "--" expression_item -> pre_dec_expression
  | expression_item "++" -> post_inc_expression
  | expression_item "--" -> post_dec_expression
  | expression_item "+=" literal -> plus_equal_expression
  | expression_item "-=" literal -> minus_equal_expression
  | expression_item "?" expression_item ":" expression_item -> ternary_expression
  | expression_item "&&" expression_item -> and_expression
  | expression_item "||" expression_item -> or_expression
  | expression_item arithmetic_operator expression_item -> arithmetic_expression
  | expression_item relational_operator expression_item -> relational_expression

// member index = obj[index]
// member dot = obj.member

// [ei]([ei])* atau ([ei])+
//member_index_expression: expression_item "[" expression_item "]" ("[" expression_item "]")*
member_index_expression: expression_item ("[" expression_item "]")+

// nama.nama(.nama)* atau nama (.nama)+
//member_dot_expression: nama_tanpa_dot "." nama_tanpa_dot ("." nama_tanpa_dot)*
member_dot_expression: nama_tanpa_dot ("." nama_tanpa_dot)+

"""
from .function_call import function_call
from .literal import literal
from .operator import operator
from .range_expression import range_expression

expression_item = f"""
{expression_item_header}

{function_call}

{operator}

{literal}

{range_expression}
"""
