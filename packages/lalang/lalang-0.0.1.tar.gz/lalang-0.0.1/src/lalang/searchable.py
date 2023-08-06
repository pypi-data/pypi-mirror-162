searchable = """
// I`satu dua tiga -empat -lima enam`
searchable: searchable_kw search_term searchable_kw
search_term: HURUF_SEARCHABLE

HURUF_SEARCHABLE: ("_"|LETTER|DIGIT) 	("_"|LETTER|DIGIT|"."|"-"|"+"|"@"|" ")*
"""
