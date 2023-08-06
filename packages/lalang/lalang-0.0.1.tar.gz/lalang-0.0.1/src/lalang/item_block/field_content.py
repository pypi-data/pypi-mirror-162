field_content = """
// sementara belum ada inisialisasi field
// mungkin perlu? tinggal tambah declaration_value? di ts bisa: https://www.typescriptlang.org/docs/handbook/2/classes.html
// tambah declaration_value? agar bisa inisialisasi field spt di ts

// dart: int? _private; yg nullable blm kehandle
// nama_jenis_identifier_nullable: nama_identifier "?" tipe_identifier
// baru dipake di funcparam utk funcdecl

field_content: field_config? field_name tipe_identifier? declaration_value?

field_config: "/" fieldconfiglist "/"
fieldconfiglist: fieldconfig ("," fieldconfig)*
// static
// final
// decorated: @Field()
fieldconfig: "+" -> public
  | "-" -> private
  | "#" -> protected
  | "ro" -> read_only       // readonly name: string = "world"; hanya assign dlm ctor
  | "%" -> static
  | "F" -> final
  | "L" -> late

field_name: HURUF_DIGIT

field_name_type: nama_identifier tipe_identifier? -> non_nullable_field
  | nama_jenis_identifier_nullable -> nullable_field
"""
