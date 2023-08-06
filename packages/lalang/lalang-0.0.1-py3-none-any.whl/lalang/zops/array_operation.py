array_operation = """

array_operation:        penanda "A" array_operation_choice
// lst?A
array_operation_choice: "/" BILBUL -> item_at       // mylist?A/5 = get item at index
  | "/" BILBUL "=" expression_item -> item_at_set   // mylist[n] = value
  | "0/" -> item_first
  | "9/" -> item_last
  | "44" nama_identifier? -> array_traversal_for_traditional // myarr?A44
  | "4@" nama_identifier? -> array_traversal_for_each
  | "4#" nama_identifier? -> array_traversal_for_key
  | "4$" nama_identifier? -> array_traversal_for_value
  | "n" array_new_operation? -> new_array
  | "+=" expression_item  ("," expression_item)* -> concat_extend_update   // mylist?A+=   another list  (extend/update)
  | "+" expression_item   -> insert_at_tail         // mylist?A+    item          (insert_at_tail)
  | "+<" expression_item  -> insert_at_head
  | "+" expression_item "@" BILBUL -> insert_at_index
  | "|"                   -> length                 // mylist?A|
  | "#" expression_item   -> count
  | "i/" nama_identifier_or_literal -> index_of // mylist?Ai/5 = get index of item (item bisa id, atau literal spt 42 dan "hello")
  | "P" BILBUL?           -> pop_item       // remove at tail
  | "S" BILBUL?           -> shift_item     // remove at head
  | "X" BILBUL ("/" BILBUL)? -> slice_array
  | "-@" BILBUL           -> remove_at_index
  | "-<"                  -> remove_at_head
  | "->"                  -> remove_at_tail
  | "-" expression_item                 -> remove_by_value
  | "+S-" BILBUL "/" BILBUL "/" expression_item ("," expression_item)* -> splice_add_remove
  | "-S-" BILBUL "/" BILBUL -> splice_remove
  | "<<"                  -> min
  | ">>"                  -> max
  | "=="                  -> average
  | "++"                  -> sum
  | "~" expression_item   -> contains
  | "~~" expression_item  -> has_key // js dan dart, array bs punya key/index
  | "0"                   -> clear
  | "0?"                  -> is_empty         // mylist?A0?
  | "2s" -> to_string                         // ', '.join(mylist) = default by himpitkan
  | "2D" -> to_dict     // dart punya asMap(), mungkin java/kt jg
  | "sp" ("/" HURUF_SYSTEM "/")? -> split     // maksudnya join...
  | "!"                   -> reverse
  | "$"                   -> sort
  | "$!"                  -> reverse_sort
  | "M#" anonymous_function   -> array_map // mylist?AM#...
  | "F#" anonymous_function   -> array_filter
  | "R#" anonymous_function   -> array_reduce
  | "A?"                      -> is_array
  | "U"                       -> uniqify

// TODO: any(predicate), all(predicate)

array_new_operation: "@" BILBUL -> allocate // ?An@10, int[] intArray = new int[10];
  | "@@" BILBUL -> allocate_with_cap // ?An@10/1000
  | "@" -> just_create
  | "$" expression_item -> initialize // ?An$...ei...
  | "$" BILBUL tipe_identifier -> initialize_with_faker // ?An$5:s, ?An$5:i
  | "F" mapper_function_for_arraylike -> create_with_arrayfrom // ?AnF(){}, ?AnF:(){}
  | "@F" BILBUL "/" BILBUL -> allocate_with_arrayfrom // ?An@F5/0

mapper_function_for_arraylike: anonymous_function
"""
