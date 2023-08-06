for_statement = """
for_statement: for_keyword for_config? condition_for condition_body

for_keyword: "/4"
  | "for"

// harus bisa handle: for, for each, for in, for of
// for i=0; i<expession; i++
// for-each item,key of array
// for-in key of array
// for-of item of array

condition_for: for_variation
for_variation: "(" for_traditional ")"  // for(i=0;i<dict.length;i++)
  |  "(" for_while? ")" -> for_ever // for(i<10), for()
  | "@" for_each "@"  // for@item/items/index@ = for key,value
  | "#" for_in "#"    // for#key/items# = for key/index
  | "$" for_of "$"    // for$item/items$ = for value

// apa gak mendingan: for(name,start,end,step) => for(index,0,42,2)
for_traditional: for_start ";" for_end (";" for_step)?
for_while: expression_item
for_each: item_name "/" array_name ("/" key_name)?
for_in: key_name "/" array_name
for_of: item_name "/" array_name

//for_start: key_name "=" expression_item
for_start: nama_jenis_identifier_optional "=" expression_item
for_end: expression_item
for_step: expression_item

key_name: nama_jenis_identifier_optional
item_name: nama_jenis_identifier_optional
array_name: nama_identifier
  | expression_item

for_config: "[" for_config_items "]"
for_config_items: for_config_item ("," for_config_item)*
// gunakan for-traditional, create local var, use nonlocal var, for-in, for-of
for_config_item: "c"
"""
