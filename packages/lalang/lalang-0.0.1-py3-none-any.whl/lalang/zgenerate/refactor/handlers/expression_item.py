from app.transpiler.zgenerate.refactor.handlers import (
    anonymous_function, arithmetic_expression, casting_expression,
    function_call, literal, member_dot_expression, member_index_expression,
    range_expression, relational_expression, ternary_expression)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def expression_item(tree, language="py"):
    kembali = ""
    provided_expression = child1(tree)
    hasil = ""
    if data(provided_expression) == "literal":
        hasil = literal.literal(provided_expression, language=language)
        # print('ei literal', type(literal), type(provided_expression), type(language), '=>', hasil)
    elif data(provided_expression) == "nama_identifier":
        hasil = token(provided_expression)
        # print('ei nama identifier:', hasil)
    elif data(provided_expression) == "relational_expression":
        hasil = relational_expression.relational_expression(
            provided_expression, language=language
        )
        # print('ei relational_expression', type(literal), type(provided_expression), type(language), '=>', hasil)
    elif data(provided_expression) == "function_call":
        hasil = function_call.function_call(provided_expression, language=language)
    elif data(provided_expression) == "arithmetic_expression":
        hasil = arithmetic_expression.arithmetic_expression(
            provided_expression, language=language
        )
    elif data(provided_expression) == "casting_expression":
        hasil = casting_expression.casting_expression(
            provided_expression, language=language
        )
    elif data(provided_expression) == "range_expression":
        hasil = range_expression.range_expression(
            provided_expression, language=language
        )
    elif data(provided_expression) == "member_index_expression":
        hasil = member_index_expression.member_index_expression(
            provided_expression, language=language
        )
    elif data(provided_expression) == "member_dot_expression":
        hasil = member_dot_expression.member_dot_expression(
            provided_expression, language=language
        )
    elif data(provided_expression) == "ternary_expression":
        # print('panggil ternary_expression dari expression_item')
        hasil = ternary_expression.ternary_expression(
            provided_expression, language=language
        )
    elif data(provided_expression) == "anonymous_function":
        hasil_in_dict = anonymous_function.anonymous_function(
            provided_expression, language=language
        )
        hasil = (
            hasil_in_dict["internal"]
            if hasil_in_dict["internal"]
            else hasil_in_dict["external"]
        )

    kembali += hasil

    if language == "py":
        pass
    elif language == "ts":
        pass
    elif language == "rs":
        pass
    elif language == "java":
        pass
    elif language == "kt":
        pass
    elif language == "go":
        pass
    elif language == "rb":
        pass
    elif language == "v":
        pass
    elif language == "dart":
        pass
    elif language == "cpp":
        pass
    elif language == "cs":
        pass
    elif language == "hs":
        pass
    elif language == "clj":
        pass
    elif language == "scala":
        pass
    elif language == "php":
        pass
    elif language == "swift":
        pass
    elif language == "elixir":
        pass
    elif language == "erlang":
        pass
    return kembali
