dataframe_operation = """
dataframe_operation:    penanda "#" dataframe_operation_config? dataframe_operation_cmd
// sementara bebas krn gak tau batas2 operasinya
dataframe_operation_cmd: HURUF_DIGIT

dataframe_operation_config: "/" dataframe_operation_config_items "/"
dataframe_operation_config_items: dataframe_operation_config_item ("," dataframe_operation_config_item)*
dataframe_operation_config_item: "c"
"""
