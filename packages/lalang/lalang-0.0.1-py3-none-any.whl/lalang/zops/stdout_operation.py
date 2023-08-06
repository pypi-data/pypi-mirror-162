stdout_operation = """

// ?+ utk stdout dan stderr dan logging...

stdout_operation: penanda "+" io_operation_choice operation_config?
// entah siapa butuh: function_call_param?

io_operation_choice: "h" -> hello
  | expression_item       -> console_log      // ?+
  | "e>" expression_item   -> console_err     // ?+|
  | "s>" expression_item   -> sprintf         // ?+s| fmt.Sprint(..)
  | "i|" expression_item   -> logging_info    // ?+i|
  | "d|" expression_item   -> logging_debug   // ?+d|
  | "w|" expression_item   -> logging_warning // ?+w|
  | "e|" expression_item   -> logging_error   // ?+e|
"""
