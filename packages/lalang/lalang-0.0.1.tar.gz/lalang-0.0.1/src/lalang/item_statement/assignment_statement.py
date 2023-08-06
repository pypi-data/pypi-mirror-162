# perlu handle destructure object, tuple, list
# =/satu,dua,tiga,empat,lima,enam/sumber/
assignment_statement = """
assignment_statement: nama_identifier assignment_config? "=" expression_item
assignment_config: ":" -> assignment_initialize // di v lang a = 42 vs a := 42
"""
