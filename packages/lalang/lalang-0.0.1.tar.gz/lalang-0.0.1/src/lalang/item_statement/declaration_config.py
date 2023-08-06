declaration_config = """

// mutable dan immutable sudah dihandle oleh $ dan %
// $ pasti mutable let mut myvar = value;
declaration_config: "/" declarationconfiglist "/"

//declaration_config: declarationconfiglist
declarationconfiglist: declare_config ("," declare_config)*

// instance field, static field
// $stack=[]
declare_config: "+" -> public
  | "-" -> private
  | "#" -> protected
  | "%" -> static
  | "L" -> late
  | "F" -> final

declaration_name: HURUF_DIGIT

declaration_value: "=" expression_item

"""
