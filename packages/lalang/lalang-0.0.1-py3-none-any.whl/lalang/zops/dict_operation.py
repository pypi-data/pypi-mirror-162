dict_operation = """
// https://www.w3schools.com/python/python_ref_dictionary.asp
// https://www.collectionsjs.com/dict
dict_operation:         penanda "D" dict_operation_choice
dict_operation_choice: "/" expression_item ("/" expression_item)? -> get_item     // with default  
  | "+=" expression_item            -> concat_extend_update       // mydict?D++   another list  (extend/update)
  | "+" expression_item "=" expression_item -> assign   // mydict?D+1=nilai
  | "|"                             -> length
  | "~(" expression_item ")"      -> has_item     // has value
  | "-(" expression_item ")"      -> remove_item  // remove by value
  | "~" expression_item           -> has_key
  | "-" expression_item           -> remove_key
  | "-@" BILBUL             -> remove_at_index
  | "->"                    -> remove_at_tail
  | "0"                   -> clear
  | "0?"                  -> is_empty   // mydict?D0?
  | "@"                   -> entries  // gaya for-each, mydict?D@
  | "#"                   -> keys     // gaya for-in, mydict?D#
  | "$"                   -> values   // gaya for-of, mydict?D$
  | "n" dict_new_operation? -> new_dict

// kvs := map[string]string{"a": "apple", "b": "banana"}
dict_new_operation: "@" -> just_create
  | "@" BILBUL tipe_data_nilai? tipe_data_kunci?-> allocate
  | "$" named_values -> initialize
  | "$" BILBUL tipe_identifier -> initialize_with_faker

tipe_data_nilai: tipe_identifier
tipe_data_kunci: tipe_identifier
"""

# ada juga fromkeys
# https://www.w3schools.com/python/ref_dictionary_fromkeys.asp
# dik.fromkeys(tuple_of_keys, default_value)

# ada juga copy
# https://www.w3schools.com/python/ref_dictionary_copy.asp
# ini spt clone
