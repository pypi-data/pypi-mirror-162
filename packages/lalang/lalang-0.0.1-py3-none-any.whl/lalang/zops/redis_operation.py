# ?r
redis_operation = """
redis_operation: penanda "r" redis_operation_config? redis_cmd (redis_key ("=" redis_value)?)?

redis_operation_config: "/" redis_operation_config_items "/"
redis_operation_config_items: redis_operation_config_item ("," redis_operation_config_item)*
redis_operation_config_item: "h=" HURUF_DIGIT -> redis_host_config
  | "p=" HURUF_DIGIT -> redis_port_config
  | "d=" HURUF_DIGIT -> redis_dbname_config
  | "s=" HURUF_DIGIT -> redis_schema_config
  | "u=" HURUF_DIGIT -> redis_username_config
  | "pw=" HURUF_DIGIT -> redis_password_config

redis_cmd: "c" -> redis_connect       // ?r/d=7/c
  | "r" -> redis_reset                // ?rr          = reset connection to default
  | "?" -> redis_exists         // ?r?key       does redis key exist?
  | "=" -> redis_keys           // ?r=*  
  | "s=" -> redis_string_get    // ?rs=key
  | "s+" -> redis_string_add    // ?rs+key=value
  | "s-" -> redis_string_del    // ?rs-key
  | "A+" -> redis_list_add      // ?rA+
  | "A-" -> redis_list_del      // ?rA-
  | "A=" -> redis_list_get      // ?rA=
  | "D+" -> redis_hash_add      // ?rD+
  | "D-" -> redis_hash_del      // ?rD-
  | "D=" -> redis_hash_get      // ?rD=
  | "S+" -> redis_set_add       // ?rS+
  | "S-" -> redis_set_del       // ?rS-
  | "S=" -> redis_set_get       // ?rS=

redis_args: redis_arg ("," redis_arg)*
redis_arg: redis_key
  | redis_value

redis_key: HURUF_EXPORT
// sementara gini dulu...tapi nanti butuh value utk dict etc
redis_value: HURUF_EXPORT 
"""
