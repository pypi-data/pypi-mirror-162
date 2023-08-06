huruf = """

HURUF_DIGIT_ONLY:       ("_"|LETTER|DIGIT) 	("_"|LETTER|DIGIT)*
HURUF_DIGIT: 						("_"|LETTER|DIGIT) 	("_"|LETTER|DIGIT|".")*
HURUF_EXPORT: 					("_"|LETTER|DIGIT|"*") 	("_"|LETTER|DIGIT|"."|"/"|"*")*
HURUF_DIGIT_DOT:				("_"|LETTER|DIGIT|".") 	("_"|LETTER|DIGIT|"."|"@"|"/")*
HURUF_DIGIT_SPASI: 			("_"|LETTER|DIGIT|"*") 	("_"|LETTER|DIGIT|"."|"@"|" "|"*")*
HURUF_DIGIT_MINUSPLUS: 	("_"|LETTER|DIGIT) 	("_"|LETTER|DIGIT|"."|"-"|"+"|"@")*
HURUF_TEMPLATESTRING:   ("_"|LETTER|DIGIT|"/") 	("_"|LETTER|DIGIT|" "|"."|","|"-"|"+"|"/"|"@")*
HURUF_SPACE: 						("_"|LETTER) 		("_"|LETTER|DIGIT|" ")*
HURUF_COMMA: 						("_"|LETTER) 		("_"|LETTER|DIGIT|",")*
HURUF_SYSTEM: 					("_"|LETTER|DIGIT|"*"|"/"|"."|"\\"") 	(LETTER|DIGIT|"_"|"*"|"."|"/"|"-"|"+"|" "|":"|"\\"|"\"")*
HURUF_PASSWORD: 				("_"|LETTER) ("_"|LETTER|DIGIT|" "|"&"|"%%"|"."|","|"-"|"_"|"+"|"@"|"#"|"*")*
HURUF_HOST: 						("_"|LETTER|DIGIT) ("_"|LETTER|DIGIT|"."|"@")*

HURUF_DIGIT_DESTRUCTURING: ("_"|LETTER|DIGIT) 	("_"|LETTER|DIGIT|".")*
"""
