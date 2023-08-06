from app.transpiler.zgenerate.refactor.handlers import (
    anonymous_function, array_map, expression_item, initialize_with_faker,
    stringify_anonymous_function_result)
from app.transpiler.zgenerate.refactor.handlers.common import (dec, inc,
                                                               self_tab)
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def array_operation(tree, identifier, language="py"):
    kembali = ""

    for item in anak(tree):
        """
        array_filter, array_reduce
        """
        if data(item) == "penanda":
            pass
        elif data(item) == "item_at":
            # lst?A/5
            at = token(item)
            kembali += f"{identifier}[{at}]"
        elif data(item) == "item_at_set":
            # lst?A/5=nilai_baru
            at = token(item)
            ei = child2(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}[{at}] = {hasil}"
        elif data(item) == "index_of":
            nama_identifier_or_literal = child1(item)
            hasil = nama_identifier_or_literal(
                nama_identifier_or_literal, language=language
            )
            # kembali += f'{identifier}.index({hasil})'
            kembali += f"{identifier}.indexOf({hasil})"
        elif data(item) == "slice_array":
            slice_startingpos = token(item)
            if jumlahanak(item) == 2:
                slice_endingpos = token(item, 1)
                kembali += f"{identifier}.slice({slice_startingpos}, {slice_endingpos})"
            else:
                kembali += f"{identifier}.slice({slice_startingpos})"
        elif data(item) == "insert_at_tail":
            """
            ini adlh standard push/append
            myvec.push(42) di rust
            mylist.append(42) di py

            lst?A+  ei
            arr?A+42
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.push({hasil})"
        elif data(item) == "concat_extend_update":
            """
            lst?A+= ei
            lst?A+= [42]
            list += [42]
            """
            eis = []
            # ei = child1(item)
            # hasil = expression_item(ei)
            for ei in anak(item):
                thing = expression_item.expression_item(ei, language=language)
                eis.append(thing)
            hasil = ", ".join(eis)
            kembali += f"{identifier}.concat({hasil})"
        elif data(item) == "insert_at_head":
            """
            lst?A+< ei
            lst?A+< 42
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            # atau identifier = [hasil] + identifier
            kembali += f"{identifier}.unshift({hasil})"
        elif data(item) == "insert_at_index":
            """
            insert_at_index
              expression_item
                nama_identifier       item
              5
            insert_at_index
              expression_item
                literal
                  literal_number      42
              5
            lst?A+ ei @5
            lst?A+ myitem @5
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)

            posisi = token(item, 1)  # child no 2 adlh token
            kembali += f"{identifier}.insert({posisi}, {hasil})"
        elif data(item) == "length":
            """
            len(arr)
            lst?A|
            """
            kembali += f"{identifier}.length"
        elif data(item) == "remove_at_index":
            """
            lst?A-5
            del arr[5]
            arr.pop(5)
            """
            posisi = token(item)
            # kembali += f'{identifier}.pop({hasil})'
            kembali += f"delete {identifier}[{hasil}]"
        elif data(item) == "splice_add_remove":
            # "+S-" BILBUL "/" BILBUL "/" expression_item ("," expression_item)*
            start_removepos = token(item)
            howmany_removeitem = token(item, 1)
            eis = []
            for ei in anak(item)[2:]:
                hasil = expression_item.expression_item(ei, language=language)
                eis.append(hasil)
            added_things = ", ".join(eis)
            kembali += f"{identifier}.splice({start_removepos}, {howmany_removeitem}, {added_things})"
        elif data(item) == "splice_remove":
            # "-S-" BILBUL "/" BILBUL
            start_removepos = token(item)
            howmany_removeitem = token(item, 1)
            kembali += f"{identifier}.splice({start_removepos}, {howmany_removeitem})"
        elif data(item) == "pop_item":
            posisi = 0
            # if beranak(item):
            #   posisi = token(item)
            #   kembali += f'{identifier}.pop({posisi})'
            # else:
            kembali += f"{identifier}.pop()"
        elif data(item) == "shift_item":
            # kembali += f'item = {identifier}[0]; del {identifier}[0]'
            kembali += f"{identifier}.shift()"
        elif data(item) == "remove_at_head":
            """
            arr?A-<
            """
            # kembali += f'{identifier}.pop(0)'
            kembali += f"del {identifier}[0]"
        elif data(item) == "remove_at_tail":
            """
            arr?A->
            """
            # kembali += f'{identifier}.pop(-1)'
            # kembali += f'{identifier}.pop()'
            kembali += f"del {identifier}[-1]"
        elif data(item) == "remove_by_value":
            """
            arr?A-ei
            """
            ei = child1(item)
            thing = expression_item.expression_item(ei, language=language)
            # index = identifier.indexOf(item)
            # if (index != -1) { identifier.splice(index, 1) }
            kembali += f"{identifier}.filter(item => item !== {thing})"
        elif data(item) == "min":
            """
            arr?A<<
            """
            kembali += f"Math.min.apply(null, {identifier})"
        elif data(item) == "max":
            """
            arr?A>>
            """
            kembali += f"Math.max.apply(null, {identifier})"
        elif data(item) == "average":
            """
            arr?A==
            """
            kembali += f"round(sum({identifier})/len({identifier}), 2)"
        elif data(item) == "sum":
            """
            arr?A++
            """
            kembali += f"sum({identifier})"
        elif data(item) == "contains":
            """
            arr?A~item
            arr?A~42
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            # kembali += f'{hasil} in {identifier}'
            kembali += f"{identifier}.includes({hasil})"
        elif data(item) == "count":
            """
            arr?A#item
            arr?A#42
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.count({hasil})"
        elif data(item) == "clear":
            """
            arr?A0
            """
            kembali += f"{identifier}.clear()"
        elif data(item) == "is_empty":
            """
            arr?A0?
            """
            kembali += identifier
        elif data(item) == "to_string":
            """
            arr?A2s
            """
            kembali += f"{identifier}.toString()"
        elif data(item) == "split":
            """
            arr?Asp
            arr?Asp/hurufsystem/
            """
            if beranak(item):
                nilai = token(item)
                kembali += f'{identifier}.join("{nilai}")'
            else:
                kembali += f'{identifier}.join(" ")'
        elif data(item) == "reverse":
            """
            arr?A!
            """
            # kembali += f'{identifier} = {identifier}[::-1]'
            # for i in reversed(iterator)
            kembali += f"{identifier}.reverse()"
        elif data(item) == "sort":
            """
            arr?A$
            ada juga numeric sort:
            const points = [40, 100, 1, 5, 25, 10];
            points.sort(function(a, b){return a - b});
            """
            kembali += f"{identifier}.sort()"
        elif data(item) == "reverse_sort":
            """
            arr?A$!
            """
            kembali += f"{identifier}.sort(reverse=True)"
        elif data(item) == "array_map":
            """
            arr?AM#(){}
            """
            kembali = array_map.array_map(item, language=language)
            kembali["operation"] = "map"
        elif data(item) == "array_filter":
            """
            arr?AF#(){}
            """
            kembali = array_map.array_map(
                item, language=language
            )  # sementara belum array_filter
            kembali["operation"] = "filter"
        elif data(item) == "array_reduce":
            """
            arr?AR#(){}
            """
            kembali = array_map.array_map(
                item, language=language
            )  # sementara belum array_reduce
            kembali["operation"] = "reduce"
        elif data(item) == "item_first":
            # "0/" -> item_first
            kembali += f"{identifier}[0]"
        elif data(item) == "item_last":
            # "9/" -> item_last
            kembali += f"{identifier}[-1]"
        elif data(item) == "array_traversal_for_traditional":
            # "44" nama_identifier? -> array_traversal_for_traditional
            iden = "item"
            if beranak(item) and chdata(item) == "nama_identifier":
                iden = chtoken(item)
            inc()
            kembali += (
                f"for index, {iden} in enumerate({identifier}):\n{self_tab()}pass"
            )
            dec()
        elif data(item) == "array_traversal_for_each":
            # "4@" nama_identifier? -> array_traversal_for_each
            iden = "item"
            if beranak(item) and chdata(item) == "nama_identifier":
                iden = chtoken(item)
            inc()
            kembali += (
                f"for index, {iden} in enumerate({identifier}):\n{self_tab()}pass"
            )
            dec()
        elif data(item) == "array_traversal_for_key":
            # "4#" nama_identifier? -> array_traversal_for_key
            iden = "index"
            if beranak(item) and chdata(item) == "nama_identifier":
                iden = chtoken(item)
            inc()
            kembali += f"for {iden},_ in enumerate({identifier}):\n{self_tab()}pass"
            dec()
        elif data(item) == "array_traversal_for_value":
            # "4$" nama_identifier? -> array_traversal_for_value
            iden = "item"
            if beranak(item) and chdata(item) == "nama_identifier":
                iden = chtoken(item)
            inc()
            kembali += f"for {iden} in {identifier}:\n{self_tab()}pass"
            dec()

        elif data(item) == "is_array":
            # myarr?AA?
            kembali += f"Array.isArray({identifier})"
        elif data(item) == "uniqify":
            # myarr?AU
            kembali += f"const {identifier} = Array.from(new Set({identifier}))"

        elif data(item) == "new_array":
            # "n" array_new_operation? -> new_array
            #     "@" BILBUL -> allocate
            #     "$" expression_item -> initialize
            #     "$" BILBUL tipe_identifier -> initialize_with_faker
            # /py/myarr?An@5
            # /py/myarr?An$[1,2,3,4,5]
            for cucu in anak(item):
                jenis = data(cucu)
                if jenis == "allocate":
                    jumlah = token(cucu)
                    # print('jumlah:', jumlah)
                    jumlah = int(jumlah)
                    kembali += f"{identifier} = {[0]*jumlah}"
                elif jenis == "initialize":
                    ei = child1(cucu)
                    hasil = expression_item.expression_item(ei, language=language)
                    print("initialize=>", hasil, type(hasil))
                    kembali += f"{identifier} = {hasil}"
                elif jenis == "initialize_with_faker":
                    hasil = initialize_with_faker.initialize_with_faker(
                        cucu, language=language
                    )
                    kembali += f"{identifier} = {hasil}"
                elif jenis == "create_with_arrayfrom":
                    # lst?AnF(){?+'hello'}
                    mapper_function_for_arraylike = child1(cucu)
                    _anonymous_function = child1(mapper_function_for_arraylike)
                    mapper_func = anonymous_function.anonymous_function(
                        _anonymous_function, language=language
                    )
                    mapper_func = stringify_anonymous_function_result.stringify_anonymous_function_result(
                        mapper_func, language=language
                    )
                    kembali += f"const {identifier} = Array.from(some_arraylike_object, {mapper_func})"
                elif jenis == "allocate_with_arrayfrom":
                    # lst?An@F5/0
                    # buat array sepanjang 5 berisi 0 setara [0,0,0,0,0]
                    panjang = token(cucu)
                    value = token(cucu, 1)
                    kembali += f"const {identifier} = Array.from({{ {panjang} }}, () => {value})"

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
