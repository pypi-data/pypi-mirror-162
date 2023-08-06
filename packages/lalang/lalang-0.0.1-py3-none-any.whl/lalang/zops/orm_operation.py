# kita pengen dg gampang oprek redis...ini sbg ganti redis language
# rdbms -> isud + create db/user/role/table/view/index + alter table/column
# redis op: string, list, hash/dict, set
orm_operation = """
orm_operation:          penanda "O" orm_operation_config orm_operation_choice

// ?O/h=...,p=...,u=...,passwd=...,d=...,s=.../
orm_operation_config: "/" orm_operation_config_items "/"
orm_operation_config_items: orm_operation_config_item ("," orm_operation_config_item)*
orm_operation_config_item: "h=" HURUF_DIGIT -> orm_host_config
  | "p=" HURUF_DIGIT -> orm_port_config
  | "d=" HURUF_DIGIT -> orm_dbname_config
  | "s=" HURUF_DIGIT -> orm_schema_config
  | "u=" HURUF_DIGIT -> orm_username_config
  | "pw=" HURUF_DIGIT -> orm_password_config

// operasi spt Model.objects.all(), .get(id=...), .create(a=1,b=2)
orm_operation_choice: "s" -> orm_select        // ?Os
  | "f1" -> orm_find_one
  | "f1u" -> orm_find_one_and_update
  | "fn" -> orm_find_many
  | "fa" -> orm_find_all
  | "i" -> orm_insert        // ?Oi
  | "u" -> orm_update        // ?Ou
  | "d" -> orm_delete        // ?Od
  | "cd" -> orm_create_database
  | "ct" -> orm_create_table
  | "at" -> orm_alter_table
  | "ac" -> orm_alter_column
  | "cu" -> orm_create_user
  | "cr" -> orm_create_role
  | "ci" -> orm_create_index
  | "cv" -> orm_create_view
  | "cp" -> orm_create_procedure
  | "cg" -> orm_create_trigger
"""
