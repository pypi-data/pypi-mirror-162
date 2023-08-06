method_content = """
method_content: method_config? function_name tipe_identifier? function_param function_content

method_config: "/" methodconfiglist "/"
methodconfiglist: methodconfig ("," methodconfig)*
// decorated: @Override
// static
// public
methodconfig: "g" -> getter   // this method is a getter
  | "s" -> setter             // this method is a setter
  | "+" -> public
  | "-" -> private
  | "#" -> protected
  | "%" -> static     // ingat python ada class vs static yg berbeda dikit konsepnya
  | "A" -> async
  | "o" -> override   // cepat @Override etc
"""
