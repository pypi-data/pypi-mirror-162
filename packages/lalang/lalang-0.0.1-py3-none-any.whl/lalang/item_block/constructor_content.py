# >(){}
constructor_content = """

// > utk bedakan dg method
constructor_content: ">" constructor_config? function_param function_content

constructor_config: "[" constructorconfiglist "]"
constructorconfiglist: constructorconfig ("," constructorconfig)*
// termasuk ada destructor
constructorconfig: "c"
"""
