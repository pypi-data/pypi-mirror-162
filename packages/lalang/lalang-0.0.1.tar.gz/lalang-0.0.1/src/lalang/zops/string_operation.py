string_operation = """

string_operation:       penanda "s" string_operation_choice
// kita mau bikin adding newline/tab/dll segampang mungkin
string_operation_choice: "+" expression_item -> concat       // mystr?s+ ...
  | "/" BILBUL          -> char_at      // mystr?s/5
  | ">" HURUF_DIGIT     -> ends_with
  | "<" HURUF_DIGIT     -> starts_with
  | "~" HURUF_DIGIT     -> contains
  | "#" HURUF_DIGIT     -> count
  | "|"                 -> length
  | "s/" HURUF_DIGIT    -> search_index    // mystr?ss/cari
  | "ls/" HURUF_DIGIT   -> last_search_index
  | "i/" HURUF_DIGIT    -> index_of     // mystr?si/5
  | "li/" HURUF_DIGIT   -> last_index_of
  | "9?"                -> is_digit
  | "0?"                -> is_empty
  | "spc?"              -> is_space
  | "2c"                -> to_chars
  | "2i"                -> to_int
  | "2f"                -> to_float
  | "2b"                -> to_byte
  | "4b"                -> from_byte
  | "2l"                -> to_literal
  | "4l"                -> from_literal
  | "2A" -> to_array     // 'hello'.split() = default by space
  | "2L" -> to_lines
  | "sp" "/" HURUF_NON_SLASH "/" BILBUL?  -> split
  | "r" "/" expression_item "/" expression_item "/"? -> replace // mystr?sr/cari/ganti/
  | "0..." BILBUL         -> zfill
  | "...0" BILBUL         -> fillz
  | "00"                 -> trim         // mystr?s0
  | "0."                 -> ltrim
  | ".0"                 -> rtrim
  | "0." HURUF_SYSTEM                -> remove_prefix
  | ".0" HURUF_SYSTEM                -> remove_suffix
  | "u"                 -> upper        // mystr?su
  | "l"                 -> lower        // mystr?sl
  | "c"                 -> capitalize   // mystr?sc
  | "ub" BILBUL (":" BILBUL)? -> substring_with_endpos // .substring
  | "ub" BILBUL "/" BILBUL    -> substring_with_length // .substr
  | "li" BILBUL (":" BILBUL)? -> slice_with_endpos
  | "__" BILBUL ("/" HURUF_SYSTEM)? -> center
  | "<<" BILBUL ("/" HURUF_SYSTEM)? -> ljust
  | "fm:" named_values -> format // ?sfm:name=usef,gf=wieke
  | "tr:" HURUF_DIGIT "=" HURUF_DIGIT -> translate // 
  | "ma:" HURUF_DIGIT ("/" regex_match_configs)? -> regex_match

HURUF_NON_SLASH: 					(" "|LETTER|DIGIT|"*"|"."|"\\\\") 	(LETTER|DIGIT|"_"|"*"|"."|"-"|"+"|" "|":"|"\\"|"\"")*

regex_match_configs: regex_match_configs+
regex_match_config: "g" -> regex_match_global
  | "i" -> regex_match_case_insensitive

// perlu juga method: char_in_string -> if c in s
// https://youtu.be/LK7tDnzUZZM?t=271 s.find(c) != string::npos
"""
