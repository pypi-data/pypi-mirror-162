# identifier?@//perintah
react_operation = """
react_operation: penanda "@" react_operation_config? react_operation_cmd
react_operation_cmd: hook_operation
  | component_operation

// https://reactjs.org/docs/hooks-reference.html
hook_operation: "us" tipe_identifier? state_initializer? -> use_state
  | "ue" anonymous_function expression_item -> use_effect // useEffect(af, [ei])
  | "uc" nama_identifier "=" nama_identifier -> use_context
  | "ur" expression_item "=" expression_item -> use_reducer // const [state,dispatch]=uR(reducer,initState)
  | "uk" anonymous_function expression_item -> use_callback
  | "um" -> use_memo
  | "uR" -> use_ref
  | "uih" -> use_imperative_handle
  | "ule" -> use_layout_effect
  | "udv" -> use_debug_value
  | "gssp" -> get_server_side_props

state_initializer: "=" expression_item

component_operation: "fc" -> functional_component
  | "cc" -> class_component

react_operation_config: "/" react_operation_config_items "/"
react_operation_config_items: react_operation_config_item ("," react_operation_config_item)*
react_operation_config_item: "c"
"""
