# myfunc()
# myfunc/conf1,conf2()
function_call = """
function_call: function_name function_call_config? "(" argument_list* ")"

function_call_config: "/" funccallconfiglist

funccallconfiglist: funccall_config+
funccall_config: "a" -> await
"""
