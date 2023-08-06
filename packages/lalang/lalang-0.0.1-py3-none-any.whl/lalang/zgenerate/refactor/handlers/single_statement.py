from app.transpiler.zgenerate.refactor.handlers import (
    assignment_statement, const_declaration, dataops_statement_with_identifier,
    defer_statement, destructuring_statement, faker_ops, fmus_ops,
    redis_operation, return_statement, stdout_operation, throw_statement,
    typealias_declaration, var_declaration, yield_statement)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def single_statement(tree, language="py"):
    kembali = ""
    item = child1(tree)
    jenis = data(item)
    print("single_statement:", jenis)
    if data(item) == "return_statement":
        kembali += return_statement.return_statement(item, language=language)
    elif data(item) == "var_declaration":
        kembali += var_declaration.var_declaration(item, language=language)
    elif data(item) == "const_declaration":
        kembali += const_declaration.const_declaration(item, language=language)
    elif data(item) == "assignment_statement":
        kembali += assignment_statement.assignment_statement(item, language=language)
    elif data(item) == "stdout_operation":
        kembali += stdout_operation.stdout_operation(item, language=language)
    elif data(item) == "typealias_declaration":
        kembali += typealias_declaration.typealias_declaration(item, language=language)
    elif data(item) == "faker_ops":
        kembali += faker_ops.faker_ops(item, language=language)
    elif data(item) == "fmus_ops":
        kembali += fmus_ops.fmus_ops(item, language=language)
    elif data(item) == "redis_operation":
        kembali += redis_operation.redis_operation(item, language=language)
    elif data(item) == "dataops_statement_with_identifier":
        kembali += dataops_statement_with_identifier.dataops_statement_with_identifier(
            item, language=language
        )
    elif data(item) == "throw_statement":
        kembali += throw_statement.throw_statement(item, language=language)
    elif data(item) == "yield_statement":
        kembali += yield_statement.yield_statement(item, language=language)
    elif data(item) == "defer_statement":
        kembali += defer_statement.defer_statement(item, language=language)
    elif data(item) == "destructuring_statement":
        kembali += destructuring_statement.destructuring_statement(
            item, language=language
        )
    elif data(item) == "declarative_program":
        program = token(item)
        from app.transpiler.frontend.main import process_language

        kembali += process_language(program, returning=True, debug=False)

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
