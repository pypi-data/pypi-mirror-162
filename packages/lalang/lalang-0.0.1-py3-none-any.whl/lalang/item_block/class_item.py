field_method_separator = '''"|"'''

from .constructor_content import constructor_content
from .field_content import field_content
from .method_content import method_content

# mari bikin interface, abstract class, dll di sini (sementara)
class_item = f"""
class_item: "@" class_config? class_name class_content

// public
// implements interface x
// extends class x
// export
// decorated: @InputType()
class_config: "/" classconfiglist "/"
classconfiglist: classconfig ("," classconfig)*

// @/i:observable,:parent_class,@override/myclass
// bisa mult interface: @/i:satu,i:dua/myclass
// bisa juga bikin utk bantuan ini dan itu: graphql? grpc? mvc model? db table?
classconfig: "+" -> public
  | "-" -> private    // perlu utk class?
  | "#" -> protected  // perlu utk class?
  | "i" -> interface  // interface declare
  | "i+" -> interface_add // buat class decl+interface decl
  | "t" -> type_alias // kita buat juga type_alias versi single statement
  | "t+" -> type_alias  // class+type
  | "@" nama_identifier   -> decorator
  | ":" nama_identifier   -> extends
  | "i:" nama_identifier  -> implements // interface (beda i dan i: = beda func decl dan call)
  | "^" -> abstract // juga perlu final dan strictfp
  | "%" -> static
  | "F" -> final
  | "SF" -> strictfp
  | "D" -> default
  | "A" -> async
  | ">" -> explicit_default_constructor // percepat ngetik

// masukkan initializer list di sini...

// class name hrs bisa terima type parameters...
class_name: nama_identifier_with_typeparams

class_content: "{{" classcontentlist* "}}"
classcontentlist: classcontent ({field_method_separator} classcontent)*
// field content
// method content
// field dan method terbedakan dg adanya funcargs-funcbody utk method
classcontent: field_content
  | constructor_content
  | method_content
  |

{field_content}

{method_content}

{constructor_content}
"""
