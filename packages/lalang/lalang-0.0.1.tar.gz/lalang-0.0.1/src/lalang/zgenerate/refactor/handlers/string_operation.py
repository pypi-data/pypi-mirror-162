from app.transpiler.zgenerate.refactor.handlers import expression_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def string_operation(tree, identifier, language="py"):
    kembali = ""

    for item in anak(tree):
        if data(item) == "penanda":
            pass
        elif data(item) == "concat":
            """
            "+" expression_item
            """
            ei1 = child1(item)
            hasil1 = expression_item.expression_item(ei1, language=language)
            kembali += f"{identifier} + {hasil1}"
        elif data(item) == "char_at":
            """
            /5
            str?s/5
            """
            nilai = token(item)
            # kembali += f'{identifier}[{nilai}]'
            kembali += f"{identifier}.charAt({nilai})"
        elif data(item) == "zfill":
            """
            0...5
            """
            nilai = token(item)
            kembali += f"{identifier}.padStart({nilai}, 0)"
        elif data(item) == "fillz":
            """
            0...5
            """
            nilai = token(item)
            kembali += f"{identifier}.padEnd({nilai}, 0)"
        elif data(item) == "ends_with":
            """
            >hurufdigit
            """
            nilai = token(item)
            kembali += f"{identifier}.endsWith({nilai})"
        elif data(item) == "starts_with":
            """
            <hurufdigit
            """
            nilai = token(item)
            kembali += f"{identifier}.startsWith({nilai})"
        elif data(item) == "contains":
            """
            ~hurufdigit
            """
            nilai = token(item)
            # juga (nilai, startingpos)
            kembali += f"{identifier}.includes({nilai})"
        elif data(item) == "count":
            """
            arr?A#item
            arr?A#42
            """
            nilai = token(item)
            kembali += f'{identifier}.count("{nilai}")'
        elif data(item) == "length":
            """
            ?s|
            """
            kembali += f"{identifier}.length"
        elif data(item) == "search_index":
            """
            s/hurufdigit
            s/kuda
            """
            nilai = token(item)
            # kembali += f'{identifier}.index({nilai})'
            kembali += f"{identifier}.find({nilai})"
        elif data(item) == "last_search_index":
            """
            ls/hurufdigit
            ls/kuda
            """
            nilai = token(item)
            # kembali += f'{identifier}.index({nilai})'
            kembali += f"{identifier}.rfind({nilai})"
        elif data(item) == "index_of":
            """
            i/hurufdigit
            i/kuda
            """
            nilai = token(item)
            kembali += f"{identifier}.indexOf({nilai})"
            # kembali += f'{identifier}.find({nilai})'
        elif data(item) == "last_index_of":
            """
            li/hurufdigit
            https://stackoverflow.com/questions/9572490/find-index-of-last-occurrence-of-a-substring-in-a-string
            when the substring is not found, rfind() returns -1 while rindex() raises an exception ValueError (Python2 link: ValueError).
            jadi rfind lebih aman...
            """
            nilai = token(item)
            kembali += f"{identifier}.lastIndexOf({nilai})"
            # kembali += f'{identifier}.rfind({nilai})'
        elif data(item) == "is_digit":
            """
            9?
            beda isnumeric dan isdigit
            https://www.w3schools.com/python/ref_string_isnumeric.asp
            https://www.w3schools.com/python/ref_string_isdigit.asp
            """
            kembali += f"{identifier}.isdigit()"
        elif data(item) == "is_empty":
            """
            0?
            """
            kembali += f"not {identifier}"
        elif data(item) == "is_space":
            """
            spc?
            """
            kembali += f"{identifier}.isspace()"
        elif data(item) == "to_chars":
            """
            2i
            Array.from('foo'))
            """
            kembali += f'{identifier}.split("")'
        elif data(item) == "to_int":
            """
            2i
            """
            kembali += f"int({identifier})"
        elif data(item) == "to_float":
            """
            2f
            """
            kembali += f"float({identifier})"
        elif data(item) == "to_byte":
            """
            2b
            """
            kembali += f'{identifier}.encode("utf-8")'
        elif data(item) == "from_byte":
            """
            4b
            """
            kembali += f'{identifier}.decode("utf-8")'
        elif data(item) == "to_array":
            """
            "2A"
            ?s2A utk iden.split()
            """
            kembali += f"{identifier}.split()"
        elif data(item) == "to_lines":
            """
            "2A"
            ?s2A utk iden.split()
            """
            kembali += f"{identifier}.splitlines()"
        elif data(item) == "split":
            """
            "sp" "/" HURUF_SYSTEM "/" BILBUL?
            """
            delim = token(item)
            if jumlahanak(item) == 2:
                jumlahsplit = token(item, 1)
                kembali += f'{identifier}.split("{delim}", {jumlahsplit})'
            else:
                kembali += f'{identifier}.split("{delim}")'
        elif data(item) == "trim":
            """
            00
            """
            kembali += f"{identifier}.trim()"
        elif data(item) == "ltrim":
            """
            0.
            """
            kembali += f"{identifier}.ltrim()"
        elif data(item) == "rtrim":
            """
            .0
            """
            kembali += f"{identifier}.rtrim()"
        elif data(item) == "remove_prefix":
            """
            0. huruf
            """
            nilai = token(item)
            kembali += f"{identifier}.removeprefix({nilai})"
        elif data(item) == "remove_suffix":
            """
            .0 huruf
            """
            nilai = token(item)
            kembali += f"{identifier}.removesuffix({nilai})"

        elif data(item) == "upper":
            """
            u
            """
            kembali += f"{identifier}.toUpperCase()"
        elif data(item) == "lower":
            """
            l
            """
            kembali += f"{identifier}.toLowerCase()"
        elif data(item) == "capitalize":
            """
            c
            """
            kembali += f"{identifier}.capitalize()"
        elif data(item) == "slice_with_endpos":
            awal = 0
            akhir = ""  # sampai end
            awal = token(item)
            if jumlahanak(item) == 2:
                # sub5/10 kita pengen inklusif 10
                akhir = token(item, 1)  # tdk spt child, token pake index dari 0
                # akhir = chdata(item, n=2)
                if akhir.isdigit():
                    akhir = int(akhir) + 1
            if akhir:
                kembali += f"{identifier}.slice({awal}, {akhir})"
            else:
                kembali += f"{identifier}.slice({awal})"
        elif data(item) == "substring_with_endpos":
            """
            "ub" BILBUL (":" BILBUL)? -> substring_with_endpos // .substring
            substring(start, end)
            string_operation
              penanda
              substring_with_endpos     5
            mystr?sub5
            """
            # from pprint import pprint
            # pprint(item)
            awal = 0
            akhir = ""  # sampai end
            awal = token(item)
            if jumlahanak(item) == 2:
                # sub5/10 kita pengen inklusif 10
                akhir = token(item, 1)  # tdk spt child, token pake index dari 0
                # akhir = chdata(item, n=2)
                if akhir.isdigit():
                    akhir = int(akhir) + 1
            if akhir:
                kembali += f"{identifier}.substring({awal}, {akhir})"
            else:
                kembali += f"{identifier}.substring({awal})"
        elif data(item) == "substring_with_length":
            """
            "ub" BILBUL "/" BILBUL    -> substring_with_length // .substr
            substr(start, len)
            ?sub dg / berarti with panjang -> .substr
            ?sub dg : berarti with endpos -> .substring
            """
            awal = token(item)
            panjang = token(item, 1)
            result = int(awal) + int(panjang)
            kembali += (
                f"{identifier}.substr({awal}, {result})"  # kurang cantik tapi jelas
            )
        elif data(item) == "replace":
            """
            "r" "/" HURUF_DIGIT "/" HURUF_DIGIT "/"
            """
            old = child1(item)
            old = expression_item.expression_item(old, language=language)
            new = child2(item)
            new = expression_item.expression_item(new, language=language)
            kembali += f"{identifier}.replace({old}, {new})"
        elif data(item) == "center":
            """
            "_" BILBUL ("/" HURUF_SYSTEM)? -> center
            https://www.w3schools.com/python/ref_string_center.asp
            """
            lebar = 0
            karakter = ""
            lebar = token(item)
            if jumlahanak(item) == 2:
                karakter = token(item, 1)
            if karakter:
                kembali += f'{identifier}.center({lebar}, "{karakter}")'
            else:
                kembali += f"{identifier}.center({lebar})"
        elif data(item) == "ljust":
            """
            "_" BILBUL ("/" HURUF_SYSTEM)? -> center
            https://www.w3schools.com/python/ref_string_center.asp
            https://www.w3schools.com/python/ref_string_ljust.asp
            """
            lebar = 0
            karakter = ""
            lebar = token(item)
            if jumlahanak(item) == 2:
                karakter = token(item, 1)
            if karakter:
                kembali += f'{identifier}.ljust({lebar}, "{karakter}")'
            else:
                kembali += f"{identifier}.ljust({lebar})"
        elif data(item) == "format":
            """
            ?sfm:name=usef,gf=wieke
            format
              named_values
                named_value
                  nama_identifier     name
                  nilai_identifier
                    expression_item
                      nama_identifier usef
                named_value
                  nama_identifier     gf
                  nilai_identifier
                    expression_item
                      nama_identifier wieke
            https://www.w3schools.com/python/ref_string_format.asp
            txt.format(price = 49)
            """
            named_values = child1(item)
            kembali += f"{identifier}.format({named_values})"
        elif data(item) == "translate":
            """
            txt?str:abc=ABC

            https://www.w3schools.com/python/ref_string_maketrans.asp
            https://www.w3schools.com/python/ref_string_translate.asp
            mystr.translate(mystr.maketrans(pertama, kedua))
            string_operation
              penanda
              translate <- mulai dari sini
                abc <- token pertama
                ABC <- token kedua
            """
            pertama = token(item)
            kedua = token(item, 1)
            kembali += (
                f"{identifier}.translate({identifier}.maketrans({pertama}, {kedua}))"
            )

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
