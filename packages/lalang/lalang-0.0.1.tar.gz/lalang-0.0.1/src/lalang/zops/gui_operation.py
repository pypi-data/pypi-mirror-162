# identifier?u//perintah
gui_operation = """
gui_operation: penanda "u" gui_operation_config? gui_operation_cmd
gui_operation_cmd: HURUF_DIGIT

gui_operation_config: "/" gui_operation_config_items "/"
gui_operation_config_items: gui_operation_config_item ("," gui_operation_config_item)*
gui_operation_config_item: "c"
"""
