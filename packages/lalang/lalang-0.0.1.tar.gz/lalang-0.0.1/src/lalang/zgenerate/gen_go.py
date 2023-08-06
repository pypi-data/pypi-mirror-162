import traceback

from app.dirutils import here, joiner, new_filename_timestamp, tempdir
from app.printutils import print_enumerate, printex, tryex
from app.stringutils import tabify_content_space, tabify_content_tab
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)
from app.utils import env_int, tidur

peta_tipe_data = {
    "char": "string",
    "integer": "int",
    "float": "float32",
    "string": "string",
    "boolean": "bool",
    "any": "nil",
    "void": "void",
}


class Generator:
    def __init__(self, RootNode, program_context):
        self.root = RootNode
        self.program_context = program_context
        self.indentno = 0
        self.output = ""
        # self.tabspace = '\t'
        self.tabspace = "  "
        self.track_methods_for_interface = False
        self.track_methods = []

    def print(self, text):
        self.output += text

    def dedent(self):
        self.indentno -= 1 if self.indentno > 0 else 0
        return self.tabspace * self.indentno

    def indent(self):
        self.indentno += 1
        return self.tabspace * self.indentno

    def tab(self, tabno=0):
        return self.tabspace * (tabno if tabno else self.indentno)

    def tabify_content(self, content):
        tabify = [
            ("" if item.startswith("}") else self.tab()) + item
            for item in content.splitlines()
        ]
        return "\n".join(tabify)

    def dec(self):
        self.indentno -= 1 if self.indentno > 0 else 0

    def inc(self):
        self.indentno += 1

    def literal_bool(self, nilailiteral):
        # nilai = True if nilailiteral.data == 'boolean_true' else False
        nilai = "true" if nilailiteral.data == "boolean_true" else "false"
        return nilai

    def literal_number(self, nilailiteral):
        nilailiteralstr = int(nilailiteral.children[0])
        # nilailiteralstr = str(nilailiteral.children[0])
        return nilailiteralstr

    def literal_char(self, nilailiteral):
        nilailiteralstr = "'" + str(nilailiteral.children[0]) + "'"
        # self.output += f'\t\t\tketemu literal_char: {nilailiteralstr}\n'
        return nilailiteralstr

    def literal_string(self, nilailiteral):
        nilailiteralstr = '"' + str(nilailiteral.children[0]) + '"'
        # self.output += f'\t\t\tketemu literal_string: {nilailiteralstr}\n'
        return nilailiteralstr

    def template_string(self, nilailiteral):
        da_string = str(child1(nilailiteral))
        while "/" in da_string:
            da_string = da_string.replace("/", "${", 1).replace("/", "}", 1)
        nilailiteralstr = "`" + da_string + "`"
        return nilailiteralstr

    def literal_list(self, nilailiteral):
        """
        literal_list <- nilailiteral
          kadang sampai di atas sudah saja...
          *
          list_items
            *
            list_item
              expression_item
                literal
                  literal_number    value
            list_item
              expression_item
                literal
                  literal_number  2
            list_item
              expression_item
                literal
                  literal_number  3
        """
        # print('literal_list:', nilailiteral.data)
        kembalian_list = []
        if nilailiteral.children:
            """
            punya: list_items
            """
            # list_items
            list_items = nilailiteral.children[0]
            # list_item = li
            for li in list_items.children:
                ei = li.children[0]
                if ei.data == "expression_item":
                    couldbe_literal = ei.children[0]
                    if couldbe_literal.data == "literal":
                        hasil_literal = self.literal(couldbe_literal)
                        print(
                            f"literal: {hasil_literal} berjenis {type(hasil_literal)}"
                        )
                        kembalian_list.append(hasil_literal)
        else:
            """
            empty list
            """
            # self.output += '[]'
            kembalian_list = []

        return kembalian_list

    def literal_dict(self, tree):
        """
        literal_dict
          dict_items
            dict_item
              dict_item_name      a
              expression_item
                literal
                  literal_number  1
            dict_item
              dict_item_name      b
              expression_item
                literal
                  literal_number  2
        """
        items = child1(tree)
        entries = []
        for item in anak(items):
            key = token(child1(item))
            value = self.expression_item(child2(item), returning=True)
            entries.append(f"{key}: {value}")

        return "{" + ", ".join(entries) + "}"

    def literal(self, couldbe_literal):
        """
        literal
          literal_list
            literal_string    value
            literal_number    value
            literal_char      value
            list_items
              *
              list_item
                expression_item
                  literal
                    literal_number    value
          literal_dict
        """
        nilailiteral = couldbe_literal.children[0]
        kembalian_literal = None
        # print('nilailiteral:', nilailiteral)
        if nilailiteral.children:
            if nilailiteral.data == "literal_string":
                kembalian_literal = self.literal_string(nilailiteral)
            elif nilailiteral.data == "literal_char":
                kembalian_literal = self.literal_char(nilailiteral)
            elif nilailiteral.data == "literal_number":
                kembalian_literal = self.literal_number(nilailiteral)
                print(
                    f"kembalian_literal number: {kembalian_literal} berjenis {type(kembalian_literal)}"
                )
            elif nilailiteral.data == "literal_list":
                kembalian_literal = self.literal_list(nilailiteral)
            elif nilailiteral.data == "literal_dict":
                kembalian_literal = self.literal_dict(nilailiteral)
            elif nilailiteral.data == "template_string":
                kembalian_literal = self.template_string(nilailiteral)
                print(f"kembalian_literal string: {kembalian_literal}")

        elif nilailiteral.data.startswith("boolean"):
            """
            literal
              boolean_true
              boolean_false
            """
            kembalian_literal = self.literal_bool(nilailiteral)
        # elif nilailiteral.data == 'literal_list':
        #  kembalian_literal = self.literal_list(nilailiteral)

        return kembalian_literal

    def enum_member(self, tree, append_iota=False):
        """
        enum_member
          nama_identifier     satu
        enum_member
          nama_identifier     dua
          expression_item
            literal
              literal_number  2
        """
        nama, nilai = "", ""
        for item in anak(tree):
            if data(item) == "nama_identifier":
                nama = token(item)
            elif data(item) == "expression_item":
                nilai = self.expression_item(item, returning=True)
        if nilai:
            return f"{nama} = {nilai}"
        elif append_iota:
            nama = f"{nama} = iota"
        return nama

    def enum_body(self, tree):
        """
        enum_body
          enum_member_list
            enum_member
              nama_identifier     satu
            enum_member
              nama_identifier     dua
              expression_item
                literal
                  literal_number  2
            enum_member
              nama_identifier     tiga
        """
        memberlist = child1(tree)
        results = []
        for index, item in enumerate(anak(memberlist)):
            if data(item) == "enum_member":
                hasil = self.enum_member(
                    item, append_iota=True if index == 0 else False
                )
                results.append(hasil)

        results = [self.tab() + item for item in results]
        return ",\n".join(results)

    def enum_declaration(self, tree):
        """
        enum_declaration
          nama_identifier   myenum
          enum_body
        """
        nama_enum, isi_enum = "", ""
        for item in anak(tree):
            if data(item) == "nama_identifier":
                nama_enum = token(item).capitalize()
            elif data(item) == "enum_body":
                self.inc()
                isi_enum = self.enum_body(item)
                self.dec()

        # nama enum gak dipake digo
        return f"const (\n{isi_enum}\n)"

    def relational_expression(self, tree):
        """
        relational_expression
          expression_item
            nama_identifier i
          operator_less
          expression_item
            literal
              literal_number        2
        """
        kembalian = "__KIRI __OPER __KANAN"
        kiri = child1(tree)
        gantikiri = self.expression_item(kiri, returning=True)
        # print(f'{kiri} gantikiri', gantikiri)
        # expression item bisa hasilkan literal number
        kembalian = kembalian.replace("__KIRI", str(gantikiri))

        oper = child2(tree)
        if data(oper) == "operator_less":
            kembalian = kembalian.replace("__OPER", "<")
        elif data(oper) == "operator_less_equal":
            kembalian = kembalian.replace("__OPER", "<=")
        elif data(oper) == "operator_greater":
            kembalian = kembalian.replace("__OPER", ">")
        elif data(oper) == "operator_greater_equal":
            kembalian = kembalian.replace("__OPER", ">=")
        elif data(oper) == "operator_equal":
            kembalian = kembalian.replace("__OPER", "==")
        elif data(oper) == "operator_not_equal":
            kembalian = kembalian.replace("__OPER", "!=")

        kanan = child3(tree)
        gantikanan = self.expression_item(kanan, returning=True)
        # print('gantikanan', gantikanan)
        kembalian = kembalian.replace("__KANAN", str(gantikanan))
        print("relational_expression => kembalian:", kembalian)
        return kembalian

    def arithmetic_operator_to_string(self, tree):
        if data(tree) == "operator_plus":
            return "+"
        elif data(tree) == "operator_minus":
            return "-"
        elif data(tree) == "operator_mult":
            return "*"
        elif data(tree) == "operator_div":
            return "/"
        return ""

    def arithmetic_expression(self, tree):
        """
        arithmetic_expression
          expression_item
            nama_identifier x
          operator_plus
          expression_item
            nama_identifier y
        """
        kiri = self.expression_item(child1(tree), returning=True)
        oper = self.arithmetic_operator_to_string(child2(tree))
        kanan = self.expression_item(child3(tree), returning=True)
        return f"{kiri} {oper} {kanan}"

    def casting_expression(self, tree):
        """
        casting_expression
          expression_item
            nama_identifier       str
          keyword_casting
          expression_item
            nama_identifier       any
        casting_expression
          expression_item
            nama_identifier       int
          keyword_casting
          expression_item
            casting_expression
              expression_item
                nama_identifier   float
              keyword_casting
              expression_item
                nama_identifier   bool
        """
        left_ei = child1(tree)
        left = self.expression_item(left_ei, returning=True)
        kw = child2(tree)
        right_first_ei = child3(tree)
        is_nameid = data(child1(right_first_ei)) == "nama_identifier"

        # jk hanya ada 2: tipe1>>tipe2
        # utk 3: tipe1>>tipe2>>tipe3, data adlh casting_expression
        # if is_nameid:
        #   right = self.expression_item(right_first_ei, returning=True)
        #   return f'({right}){left}'

        right = self.expression_item(right_first_ei, returning=True)
        return f"{left} as {right}"

    def range_expression(self, tree):
        kembali = ""
        start, stop, step = "", "", ""
        for item in anak(tree):
            jenis = data(item)
            if jenis == "range_keyword":
                pass
            elif jenis == "range_expr_config":
                pass
            elif jenis == "range_start":
                start = token(item)
            elif jenis == "range_stop":
                stop = token(item)
            elif jenis == "range_step":
                step = token(item)
        kembali += f"{start}..{stop}"
        return kembali

    def expression_item(self, expritem, returning=True):
        """
        literal dalam expression_item bisa berbeda tipe hasilnya
        ada yg '' juga "" dan [] dst.
        """
        # literal
        literal = child1(expritem)
        hasil = ""
        if data(literal) == "literal":
            hasil = self.literal(literal)
        elif data(literal) == "nama_identifier":
            hasil = token(literal)
        elif data(literal) == "relational_expression":
            hasil = self.relational_expression(literal)
        elif data(literal) == "function_call":
            hasil = self.function_call(literal)
        elif data(literal) == "arithmetic_expression":
            hasil = self.arithmetic_expression(literal)
        elif data(literal) == "casting_expression":
            hasil = self.casting_expression(literal)
        elif data(literal) == "range_expression":
            hasil = self.range_expression(literal)
        elif data(literal) == "pre_inc_expression":
            # ini kembalikan identifier
            ei = child1(literal)
            identifier = self.expression_item(ei, returning=True)
            hasil = "++" + identifier
        elif data(literal) == "post_inc_expression":
            ei = child1(literal)
            identifier = self.expression_item(ei, returning=True)
            hasil = identifier + "++"
        elif data(literal) == "pre_dec_expression":
            # ini kembalikan identifier
            ei = child1(literal)
            identifier = self.expression_item(ei, returning=True)
            hasil = "--" + identifier
        elif data(literal) == "post_dec_expression":
            ei = child1(literal)
            identifier = self.expression_item(ei, returning=True)
            hasil = identifier + "--"

        if returning:
            return hasil
        else:
            self.output += f"{hasil}"

    def declaration_value(self, tree):
        ei = child1(tree)
        nilai_variable = self.expression_item(ei, returning=True)
        return nilai_variable

    def tipe_identifier(self, tree):
        """
        tipe_identifier
          string
        tipe_identifier
          tipe_data_buatan
            nama_identifier       n
        """
        kembali = ""
        for item in anak(tree):
            jenis = data(item)
            if jenis == "tipe_data_buatan":
                kembali = chtoken(item)
            elif jenis in [
                "array",
                "dict",
                "pair",
                "set",
                "tuple",
            ]:  # ['dataframe', 'directory', 'file', 'network', 'orm']
                if jenis == "array":
                    if beranak(item) and chdata(item) == "item_type":
                        tipeanak = chdata(
                            child(item)
                        )  # item=array / item_type / string
                        # kembali = 'Vec<' + peta_tipe_data.get(tipeanak, tipeanak) + '>'
                        kembali = "[]" + peta_tipe_data.get(tipeanak, tipeanak)
                    else:
                        kembali = "[]"
                elif jenis == "set":
                    if beranak(item) and chdata(item) == "item_type":
                        tipeanak = chdata(
                            child(item)
                        )  # item=array / item_type / string
                        kembali = f"Set<{peta_tipe_data.get(tipeanak, tipeanak)}>"
                    else:
                        kembali = "Set<?>"
                elif jenis == "dict":
                    if beranak(item) and sebanyak(item, 2):
                        """
                        | "D" (key_type "," value_type)?    -> dict
                        dict
                          key_type
                            integer
                          value_type
                            string
                        """
                        keytype = child(item, 1)
                        keytype = chdata(keytype)
                        valtype = child(item, 2)  # value_type
                        valtype = chdata(valtype)  # string
                        kunci = peta_tipe_data.get(keytype, keytype)
                        nilai = peta_tipe_data.get(valtype, valtype)
                        print("dict type:", kunci, "dan:", nilai)
                        kembali = f"map[{kunci}]{nilai}"
                    else:
                        kembali = f"map[string]string"
                elif jenis == "pair":
                    if beranak(item) and sebanyak(item, 2):
                        """ """
                        keytype = child(item, 1)
                        keytype = chdata(keytype)
                        valtype = child(item, 2)  # value_type
                        valtype = chdata(valtype)  # string
                        kunci = peta_tipe_data.get(keytype, keytype)
                        nilai = peta_tipe_data.get(valtype, valtype)
                        kembali = f"Pair<{kunci}, {nilai}>"
                    else:
                        kembali = f"Pair<?, ?>"
            else:
                jenis = data(item)
                kembali = peta_tipe_data.get(jenis, jenis)
        return kembali

    def nama_jenis_identifier_optional(self, tree):
        """
        nama_jenis_identifier_optional: nama_identifier tipe_identifier?
        nama_jenis_identifier_optional
          nama_identifier i
          tipe_identifier
            integer
        """
        nama, tipe = "", ""
        for item in anak(tree):
            if data(item) == "nama_identifier":
                nama = token(item)
            elif data(item) == "tipe_identifier":
                tipe = self.tipe_identifier(item)
        if tipe:
            return f"{nama}: {tipe}"
        return nama

    def const_declaration(self, tree, returning=True):
        """
        $str="not a number"
        const_declaration
          declaration_name        v
          declaration_value
            expression_item
              literal
                literal_dict
                  dict_items
                    dict_item
                      dict_item_name      a
                      expression_item
                        nama_identifier   d
                    dict_item
                      dict_item_name      b
                      expression_item
                        nama_identifier   whatever

        var_declaration: "$" declaration_config? declaration_name tipe_identifier? declaration_value?
        const_declaration: "%" declaration_config? declaration_name tipe_identifier? declaration_value?
        """
        # if returning:
        #   kembali = 'const '
        # else:
        #   self.print('const ')
        nama_const, jenis_const, nilai_const = "", "", ""
        for dahan in anak(tree):
            if data(dahan) == "declaration_config":
                pass
            elif data(dahan) == "declaration_name":
                nama_const = token(dahan)
            elif data(dahan) == "tipe_identifier":
                jenis_const = self.tipe_identifier(dahan)
                # if jenis_const:
                #   jenis_const = ': ' + jenis_const
            elif data(dahan) == "declaration_value":
                nilai_const = self.declaration_value(dahan)

        # if returning:
        return f"const {nama_const} {jenis_const} = {nilai_const};"
        # self.print(f'const {nama_const}{jenis_const} = {nilai_const};')

    def var_declaration(self, tree, returning=True):
        """
        $str="not a number"
        var_declaration
          declaration_name        str
          declaration_value
            expression_item
              literal
                literal_string    not a number
        $str:s="not a number"
        var_declaration
          declaration_name        str
          tipe_identifier
            string
          declaration_value
            expression_item
              literal
                literal_string    not a number
        var_declaration: "$" declaration_config? declaration_name tipe_identifier? declaration_value?
        """
        if returning:
            kembali = "var "
        else:
            self.print("var ")
        for dahan in anak(tree):
            if data(dahan) == "declaration_config":
                pass
            elif data(dahan) == "declaration_name":
                declaration_name = token(dahan)
                # if returning:
                kembali += declaration_name
                # else:
                #   self.print(declaration_name)
            elif data(dahan) == "tipe_identifier":
                # jenis = data(child1(dahan))
                # tipe_native = peta_tipe_data.get(jenis, jenis)
                tipe_native = self.tipe_identifier(dahan)
                # if returning:
                kembali += f" {tipe_native}"
                # else:
                #   self.print(f': {tipe_native}')
            elif data(dahan) == "declaration_value":
                ei = child1(dahan)
                if data(ei) == "expression_item":
                    nilai_variable = self.expression_item(ei, returning=True)
                    # if returning:
                    kembali += f" = {nilai_variable}"
                    # else:
                    #   self.print(f' = {nilai_variable}')
                elif data(ei) == "instantiation_expression":
                    """
                    $c=*MyClass()
                    """
                    # print('instantiation_expression #1')
                    hasil = self.instantiation_expression(ei, returning=True)
                    # print('instantiation_expression #2')
                    hasil = " = " + hasil  # nama = hasil
                    # if returning:
                    kembali += hasil
                    # else:
                    #   self.print(hasil)

        if returning:
            return kembali
        self.print(kembali)

    def return_statement(self, item, returning=True):
        if returning:
            kembali = f"return "
        else:
            self.print(f"return ")  # plus space

        # expression_item
        expritem = child1(item)
        if data(expritem) == "expression_item":
            output = self.expression_item(expritem, returning=returning)
            if returning:
                kembali += output

        if returning:
            return kembali

    def assignment_statement(self, tree, returning=True):
        kembali = ""
        lhs, rhs = "", ""
        for item in anak(tree):
            if data(item) == "nama_identifier":
                lhs = token(item)
            elif data(item) == "instantiation_expression":
                rhs = self.instantiation_expression(item, returning=True)
            elif data(item) == "expression_item":
                rhs = self.expression_item(item)
        kembali += f"{lhs} = {rhs}"
        return kembali

    def stdout_operation(self, tree):
        """
        ?+
        stdout_operation
          penanda
          console_log
            expression_item
              literal
                literal_string    hello
        """
        for item in anak(tree):
            # kita iterate utk antisipasi masa depan mau tambah child = config etc
            # misa utk print logger, DebugOutputString dst.
            if data(item) == "console_log":
                ei = child1(item)
                nilai = self.expression_item(ei, returning=True)
                return f"fmt.Println({nilai})"

    def object_content(self, tree):
        """
        object_content
          nama_identifier satu
          tipe_identifier
            string
        object_content
          nama_identifier dua
          tipe_identifier
            integer
        """
        nama, jenis = "", ""
        for item in anak(tree):
            if data(item) == "nama_identifier":
                nama = token(item)
            elif data(item) == "tipe_identifier":
                jenis = self.tipe_identifier(item)
        return f"{nama}: {jenis}" + ";"  # perlu ; atau , ?

    def object_type(self, tree):
        """
        object_type
          object_contents
            object_content
              nama_identifier satu
              tipe_identifier
                string
            statement_separator
            object_content
              nama_identifier dua
              tipe_identifier
                integer
        /ts/&&mytype={}
        /ts/&&mytype={satu:s;dua:i}
        /ts/@@mytype{satu:s|dua:i}
        """
        if not beranak(tree):
            return "{}"
        object_contents = child1(tree)
        contents = []
        for item in anak(object_contents):
            # ingat ada juga content = statement_separator
            if data(item) == "object_content":
                buah = self.object_content(item)
                contents.append(buah)

        kembali = "\n".join(contents)
        self.inc()
        kembali = self.tabify_content(kembali)
        self.dec()
        kembali = "{\n" + kembali + "\n}"
        return kembali

    def tipe_data_semua(self, tree):
        """
        tipe_data_semua: tipe_data_builtin
          | tipe_data_collection
          | tipe_data_fungsi
          | tipe_data_buatan
        tipe_data_semua
          array
            item_type
              string
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "array":
                kembali = self.tipe_identifier_array(item)
            elif data(item) == "object_type":
                kembali = self.object_type(item)
            else:
                jenis = data(item)
                kembali = peta_tipe_data.get(jenis, jenis)
        return kembali

    def typealias_declaration(self, tree):
        """
          typealias_declaration
            typealias_keyword
            nama_identifier mytypename
            tipe_data_semua
        /ts/&&mynewtype = As
        """
        kembali = ""
        kw, nama, nilai = "", "", ""
        for item in anak(tree):
            if data(item) == "typealias_keyword":
                kw = "type"
            elif data(item) == "nama_identifier":
                nama = token(item)
            elif data(item) == "tipe_data_semua":
                nilai = self.tipe_data_semua(item)
        kembali = f"{kw} {nama} = {nilai}"
        return kembali

    def file_operation(self, tree):
        """
        file_operation
          penanda
          json_out
            expression_item
              nama_identifier       out
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "json_out":
                ei = child1(item)
                hasil = self.expression_item(ei, returning=True)
                kembali = f"JSON.stringify({hasil})"
            elif data(item) == "json_in":
                ei = child1(item)
                hasil = self.expression_item(ei, returning=True)
                kembali = f"JSON.parse({hasil})"
        # print('kembali file/json operation:', kembali)
        return kembali

    def dict_operation(self, tree, identifier):
        """
        https://www.w3schools.com/python/python_ref_dictionary.asp
        data_operation
          dict_operation
            penanda
            ...
        /py/iden?D...
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "penanda":
                pass
            elif data(item) == "concat_extend_update":
                """
                "+=" expression_item
                concat_extend_update
                  expression_item
                    literal
                      literal_dict
                        dict_items
                          dict_item
                            dict_item_name        a
                            expression_item
                              literal
                                literal_number    1
                """
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.update({hasil})"
            elif data(item) == "get_item":
                """
                "/" literal ("/" literal)?
                iden.get(item, item)
                get_item
                  expression_item
                    nama_identifier       item
                  expression_item
                    nama_identifier       default
                """
                ei = child1(item)
                hasil1 = self.expression_item(ei)
                hasil2 = hasil1
                if jumlahanak(item) == 2:
                    ei2 = child2(item)
                    hasil2 = self.expression_item(ei2)
                kembali += f"{identifier}.get({hasil1}, {hasil2})"
            elif data(item) == "length":
                """
                dik?D|
                """
                kembali += f"len({identifier})"
            elif data(item) == "assign":
                """
                "+" expression_item "=" expression_item
                dik[item]=nilai
                dik?D+item=nilai
                """
                ei1 = child1(item)
                ei2 = child2(item)
                hasil1 = self.expression_item(ei1)
                hasil2 = self.expression_item(ei2)
                kembali += f"{identifier}[{hasil1}] = {hasil2}"
            elif data(item) == "has_item":
                """
                "~(" expression_item ")"
                """
                ei1 = child1(item)
                hasil1 = self.expression_item(ei1)
                kembali += f"{hasil1} in {identifier}.values()"
            elif data(item) == "remove_item":
                """
                "-(" expression_item ")"
                filtereddik = {k:v for k,v in identifier.items() if v != hasil}
                """
                ei1 = child1(item)
                hasil1 = self.expression_item(ei1)
                kembali += f"{{k:v for k,v in {identifier}.items() if v != {hasil1}}}"
            elif data(item) == "has_key":
                """
                "~" expression_item
                """
                ei1 = child1(item)
                hasil1 = self.expression_item(ei1)
                kembali += f"{hasil1} in {identifier}"
            elif data(item) == "remove_key":
                """
                "-" expression_item
                """
                ei1 = child1(item)
                hasil1 = self.expression_item(ei1)
                kembali += f"del {identifier}[{hasil1}]"
            elif data(item) == "clear":
                """
                dik?D0
                """
                kembali += f"{identifier}.clear()"
            elif data(item) == "remove_at_tail":
                """
                popitem = remove last inserted
                dik?D->
                """
                kembali += f"{identifier}.popitem()"
            elif data(item) == "remove_at_index":
                """
                dik?D-@5
                """
                hasil = token(item)
                kembali += f"{identifier}.pop({hasil})"
            elif data(item) == "is_empty":
                """
                dik?D0?
                """
                # kembali += f'len({identifier}) == 0'
                kembali += identifier
            elif data(item) == "entries":
                """
                dik?D@
                """
                kembali += f"{identifier}.entries()"
            elif data(item) == "keys":
                """
                dik?D#
                """
                kembali += f"{identifier}.keys()"
            elif data(item) == "values":
                """
                dik?D$
                """
                kembali += f"{identifier}.values()"
            elif data(item) == "new_dict":
                for cucu in anak(item):
                    jenis = data(cucu)
                    if jenis == "allocate":
                        """
                        iden?Dn@5
                        """
                        jumlah = token(cucu)  # token child pertama
                        jumlah = int(jumlah)
                        tipe_data_nilai = "string"  # atau int (utk values)
                        tipe_data_kunci = "string"
                        if (
                            jumlahanak(cucu) == 2
                            and chdata(cucu, 2) == "tipe_data_nilai"
                        ):
                            # ada tipe data nilai
                            tipe_identifier_untuk_nilai = child(child2(cucu))
                            tipe_data_nilai = self.tipe_identifier(
                                tipe_identifier_untuk_nilai
                            )
                            # print('oprek tipe_data_nilai', data(tipe_identifier_untuk_nilai), 'peroleh:', tipe_data_nilai)
                        elif (
                            jumlahanak(cucu) == 3
                            and chdata(cucu, 3) == "tipe_data_kunci"
                        ):
                            # ada tipe data nilai dan kunci
                            # oprek tipe nilai dulu
                            tipe_identifier_untuk_nilai = child(child2(cucu))
                            tipe_data_nilai = self.tipe_identifier(
                                tipe_identifier_untuk_nilai
                            )
                            # print('oprek tipe_data_nilai', data(tipe_identifier_untuk_nilai), 'peroleh:', tipe_data_nilai)
                            # oprek tipe kunci
                            tipe_identifier_untuk_kunci = child(child3(cucu))
                            tipe_data_kunci = self.tipe_identifier(
                                tipe_identifier_untuk_kunci
                            )
                            # print('oprek tipe_data_kunci', data(tipe_identifier_untuk_kunci), 'peroleh:', tipe_data_kunci)
                        from app.fakerutils import get_by_datatypes

                        if tipe_data_kunci == "string":
                            from string import ascii_lowercase

                            x = list(ascii_lowercase)
                            keys = [x[i] for i in range(jumlah)]
                        else:
                            keys = list(range(jumlah))

                        hasil = get_by_datatypes(
                            tipe_data_nilai, int(jumlah), as_list=True
                        )
                        # hilangkan ' dari hasil agar int 42 bukan '42', string "hell" bukan '"hell"'
                        # hasil = [item.replace("'",'') for item in hasil]
                        if tipe_data_nilai == "int":
                            hasil = [int(item) for item in hasil]
                        elif tipe_data_nilai == "string":
                            hasil = [item.replace("'", "") for item in hasil]
                        # kv = str(dict(zip(keys, hasil)))
                        print("nilai hasil/dict-value sblm kv adlh", hasil)
                        kv = dict(zip(keys, hasil))
                        print("nilai kv sblm kembali adl", kv)
                        kembali += f"{identifier} := map[{tipe_data_kunci}]{tipe_data_nilai}{kv}"
                    elif jenis == "just_create":
                        kembali += f"{identifier} := map[{tipe_data_kunci}]{tipe_data_nilai}{{}}"
                    elif jenis == "initialize":
                        ei = child1(cucu)
                        hasil = self.expression_item(ei)
                        # print('initialize=>', hasil, type(hasil))
                        kembali += f"{identifier} = {hasil}"
                    elif jenis == "initialize_with_faker":
                        # print('initialize_with_faker!')
                        hasil = self.initialize_with_faker(cucu)
                        # print('initialize_with_faker=>', hasil, type(hasil))
                        kembali += f"{identifier} = {hasil}"
        return kembali

    def string_operation(self, tree, identifier):
        """
        https://www.w3schools.com/python/python_ref_string.asp
        /py/iden?As...
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "penanda":
                pass
            elif data(item) == "concat":
                """
                "+" expression_item
                """
                ei1 = child1(item)
                hasil1 = self.expression_item(ei1)
                kembali += f"{identifier} + {hasil1}"
            elif data(item) == "char_at":
                """
                /5
                str?s/5
                """
                nilai = token(item)
                kembali += f"{identifier}[{nilai}]"
            elif data(item) == "zfill":
                """
                0...5
                """
                nilai = token(item)
                kembali += f"{identifier}.zfill({nilai})"
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
                kembali += f"{identifier}.endswith({nilai})"
            elif data(item) == "starts_with":
                """
                <hurufdigit
                """
                nilai = token(item)
                kembali += f"{identifier}.startswith({nilai})"
            elif data(item) == "contains":
                """
                ~hurufdigit
                """
                nilai = token(item)
                kembali += f"{nilai} in {identifier}"
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
                kembali += f"len({identifier})"
            elif data(item) == "search_index":
                """
                s/hurufdigit
                s/kuda
                The search() method cannot take a second start position argument.
                The indexOf() method cannot take powerful search values (regular expressions).
                """
                nilai = token(item)
                # kembali += f'{identifier}.index({nilai})'
                kembali += f"{identifier}.search({nilai})"
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
                # ada juga indexOf(c, startingpos)
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
                """
                kembali += f"list({identifier})"
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
                kembali += f"{identifier}.strip()"
            elif data(item) == "ltrim":
                """
                0.
                """
                kembali += f"{identifier}.lstrip()"
            elif data(item) == "rtrim":
                """
                .0
                """
                kembali += f"{identifier}.rstrip()"

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
                kembali += f"{identifier}.upper()"
            elif data(item) == "lower":
                """
                l
                """
                kembali += f"{identifier}.lower()"
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
                    kembali += f"{identifier}[{awal}:{akhir}]"
                else:
                    kembali += f"{identifier}[{awal}:]"
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
                kembali += f"{identifier}[{awal}:{result}]"  # kurang cantik tapi jelas
            elif data(item) == "replace":
                """
                "r" "/" HURUF_DIGIT "/" HURUF_DIGIT "/"
                """
                old = token(item)
                new = token(item, 1)
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
                kembali += f"{identifier}.translate({identifier}.maketrans({pertama}, {kedua}))"
        return kembali

    def array_map(self, tree):
        """
        map
          anonymous_function
            function_param
            anon_statements
              statement_item
                single_statement
                  stdout_operation
                    penanda
                    console_log
                      expression_item
                        literal
                          literal_string  hello
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "anonymous_function":
                kembali = self.anonymous_function(item)
        return kembali

    def array_operation(self, tree, identifier):
        """
        https://www.w3schools.com/python/ref_list_sort.asp
        /py/iden?AM#(){?+'hello'}
        """
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
                hasil = self.expression_item(ei)
                kembali += f"{identifier}[{at}] = {hasil}"
            elif data(item) == "index_of":
                nama_identifier_or_literal = child1(item)
                hasil = self.nama_identifier_or_literal(nama_identifier_or_literal)
                kembali += f"{identifier}.index({hasil})"
            elif data(item) == "slice_array":
                slice_startingpos = token(item)
                if jumlahanak(item) == 2:
                    slice_endingpos = token(item, 1)
                    kembali += (
                        f"{identifier}.slice({slice_startingpos}, {slice_endingpos})"
                    )
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
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.append({hasil})"
            elif data(item) == "concat_extend_update":
                """
                lst?A+= ei
                lst?A+= [42]
                list += [42]
                """
                eis = []
                # ei = child1(item)
                # hasil = self.expression_item(ei)
                for ei in anak(item):
                    thing = self.expression_item(ei)
                    eis.append(thing)
                hasil = ", ".join(eis)
                kembali += f"{identifier}.extend({hasil})"
            elif data(item) == "insert_at_head":
                """
                lst?A+< ei
                lst?A+< 42
                """
                ei = child1(item)
                hasil = self.expression_item(ei)
                # atau identifier = [hasil] + identifier
                kembali += f"{identifier}.insert(0, {hasil})"
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
                hasil = self.expression_item(ei)

                posisi = token(item, 1)  # child no 2 adlh token
                kembali += f"{identifier}.insert({posisi}, {hasil})"
            elif data(item) == "length":
                """
                len(arr)
                lst?A|
                """
                kembali += f"len({identifier})"
            elif data(item) == "remove_at_index":
                """
                lst?A-5
                del arr[5]
                arr.pop(5)
                """
                posisi = token(item)
                # kembali += f'{identifier}.pop({hasil})'
                kembali += f"del {identifier}[{hasil}]"
            elif data(item) == "splice_add_remove":
                # "+S-" BILBUL "/" BILBUL "/" expression_item ("," expression_item)*
                start_removepos = token(item)
                howmany_removeitem = token(item, 1)
                eis = []
                for ei in anak(item)[2:]:
                    hasil = self.expression_item(ei)
                    eis.append(hasil)
                added_things = ", ".join(eis)
                kembali += f"{identifier}.splice({start_removepos}, {howmany_removeitem}, {added_things})"
            elif data(item) == "splice_remove":
                # "-S-" BILBUL "/" BILBUL
                start_removepos = token(item)
                howmany_removeitem = token(item, 1)
                kembali += (
                    f"{identifier}.splice({start_removepos}, {howmany_removeitem})"
                )
            elif data(item) == "pop_item":
                posisi = 0
                if beranak(item):
                    posisi = token(item)
                    kembali += f"{identifier}.pop({posisi})"
                else:
                    kembali += f"{identifier}.pop()"
            elif data(item) == "shift_item":
                # kembali += f'item = {identifier}[0]; del {identifier}[0]'
                kembali += f"next(iter({identifier}))"
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
            elif data(item) == "min":
                """
                arr?A<<
                """
                kembali += f"min({identifier})"
            elif data(item) == "max":
                """
                arr?A>>
                """
                kembali += f"max({identifier})"
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
                hasil = self.expression_item(ei)
                kembali += f"{hasil} in {identifier}"
            elif data(item) == "count":
                """
                arr?A#item
                arr?A#42
                """
                ei = child1(item)
                hasil = self.expression_item(ei)
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
                kembali += f"str({identifier})"
            elif data(item) == "split":
                """
                arr?Asp
                arr?Asp/hurufsystem/
                """
                if beranak(item):
                    nilai = token(item)
                    kembali += f'"{nilai}".join({identifier})'
                else:
                    kembali += f'" ".join({identifier})'
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
                kembali += self.array_map(item)
                kembali["operation"] = "map"
            elif data(item) == "array_filter":
                """
                arr?AF#(){}
                """
                kembali += self.array_map(item)  # sementara belum array_filter
                kembali["operation"] = "filter"
            elif data(item) == "array_reduce":
                """
                arr?AR#(){}
                """
                kembali += self.array_map(item)  # sementara belum array_reduce
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
                self.inc()
                kembali += (
                    f"for index, {iden} in enumerate({identifier}):\n{self.tab()}pass"
                )
                self.dec()
            elif data(item) == "array_traversal_for_each":
                # "4@" nama_identifier? -> array_traversal_for_each
                iden = "item"
                if beranak(item) and chdata(item) == "nama_identifier":
                    iden = chtoken(item)
                self.inc()
                # for i, num := range nums {}
                kembali += f"for index, {iden} := range {identifier}:\n{self.tab()}pass"
                self.dec()
            elif data(item) == "array_traversal_for_key":
                # "4#" nama_identifier? -> array_traversal_for_key
                iden = "index"
                if beranak(item) and chdata(item) == "nama_identifier":
                    iden = chtoken(item)
                self.inc()
                kembali += f"for {iden},_ in enumerate({identifier}):\n{self.tab()}pass"
                self.dec()
            elif data(item) == "array_traversal_for_value":
                # "4$" nama_identifier? -> array_traversal_for_value
                iden = "item"
                if beranak(item) and chdata(item) == "nama_identifier":
                    iden = chtoken(item)
                self.inc()
                kembali += f"for {iden} in {identifier}:\n{self.tab()}pass"
                self.dec()
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
                    elif jenis == "just_create":
                        kembali += f"{identifier} = []"
                    elif jenis == "initialize":
                        ei = child1(cucu)
                        hasil = self.expression_item(ei)
                        # print('initialize=>', hasil, type(hasil))
                        kembali += f"{identifier} = {hasil}"
                    elif jenis == "initialize_with_faker":
                        # print('initialize_with_faker!')
                        hasil = self.initialize_with_faker(cucu)
                        # print('initialize_with_faker=>', hasil, type(hasil))
                        kembali += f"{identifier} = {hasil}"

        return kembali

    def data_operation(self, tree, identifier):
        """
        data_operation
          file_operation
            penanda
            json_out
              expression_item
                nama_identifier       out
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "file_operation":
                kembali = self.file_operation(item)
                kembali = {"type": "file_operation", "result": kembali}
            elif data(item) == "array_operation":
                kembali = self.array_operation(item, identifier)
                if isinstance(kembali, dict):
                    kembali["type"] = "array_operation"
            elif data(item) == "dict_operation":
                kembali = self.dict_operation(item, identifier)
                if isinstance(kembali, dict):
                    kembali["type"] = "dict_operation"
            elif data(item) == "set_operation":
                kembali = self.set_operation(item, identifier)
                if isinstance(kembali, dict):
                    kembali["type"] = "set_operation"
            elif data(item) == "string_operation":
                kembali = self.string_operation(item, identifier)
                if isinstance(kembali, dict):
                    kembali["type"] = "string_operation"
            elif data(item) == "datetime_operation":
                kembali = self.datetime_operation(item, identifier)
                if isinstance(kembali, dict):
                    kembali["type"] = "datetime_operation"
            elif data(item) == "gui_operation":
                kembali = self.gui_operation(item)
                if isinstance(kembali, dict):
                    kembali["type"] = "gui_operation"
            elif data(item) == "react_operation":
                kembali = self.react_operation(item, identifier)
                if isinstance(kembali, dict):
                    kembali["type"] = "react_operation"
        return kembali

    def dataops_statement(self, tree, identifier):
        """
        dataops_statement
          data_operation
            file_operation
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "data_operation":
                kembali = self.data_operation(item, identifier)
        return kembali

    def dataops_statement_with_identifier(self, tree):
        """
        /ts/mydata?Fj>out
        dataops_statement_with_identifier
          nama_identifier mydata
          dataops_statement
            data_operation
              file_operation
                penanda
                json_out
                  expression_item
                    nama_identifier       out
        """
        identifier, rhs = "", ""
        for item in anak(tree):
            if data(item) == "nama_identifier":
                identifier = token(item)
            elif data(item) == "dataops_statement":
                rhs = self.dataops_statement(item, identifier)

        print("dataops_statement_with_identifier =>", rhs, "bertipe:", type(rhs))

        if isinstance(rhs, dict):
            """
            kembalian anon func: dict berisi internal dan external
            """
            if rhs["type"] == "array_operation":
                operasi = rhs["operation"]
                if rhs["external"]:
                    kembali = (
                        f"{rhs['external']}\n{operasi}({rhs['internal']}, {identifier})"
                    )
                else:
                    kembali = f"{operasi}({rhs['internal']}, {identifier})"
            elif rhs["type"] == "file_operation":
                kembali = f'{identifier} = {rhs["result"]}'
        elif isinstance(rhs, str):
            kembali = rhs

        return kembali

    def faker_args(self, tree):
        """
        faker_args
          fake_arg      0
          fake_arg      100
        """
        args = []
        for item in anak(tree):
            if data(item) == "fake_arg":
                hasil = token(item)
                if hasil.isdigit():
                    hasil = int(hasil)
                args.append(hasil)
        # return ', '.join(args)
        return args  # biar *args

    def faker_ops(self, tree):
        """
        faker_ops
          penanda
          faker_num       10
          faker_cmd       random_int
          faker_args
            fake_arg      0
            fake_arg      100
          as_list
        faker_ops
          penanda
          faker_num       10
          faker_cmd       random_int
          faker_args
            fake_arg      0
            fake_arg      100
        /py/?K10/random_int(0,100)/A
        """
        kembali = ""
        as_list, as_string = True, False
        funcname, funcargs, callnum = "", "", 1

        # print('#1')
        for item in anak(tree):
            if data(item) == "penanda":
                pass
            elif data(item) == "faker_num":
                callnum = int(token(item))
            elif data(item) == "faker_cmd":
                funcname = token(item)
            elif data(item) == "faker_args":
                funcargs = self.faker_args(item)
            elif data(item) == "as_list":
                as_list = True
            elif data(item) == "as_string":
                as_string = True
        # print('#2, args:', funcargs)
        from langs.data.fakesey import palsu

        faker = palsu.faker
        hasil = []
        # print('#3, func', funcname)
        for i in range(callnum):
            # print('\ti:', i)
            if funcargs:
                ok = getattr(faker, funcname)(*funcargs)
                # print('\t\tok:', ok)
            else:
                ok = getattr(faker, funcname)()

            if isinstance(ok, int):
                ok = str(ok)
            elif isinstance(ok, list):
                ok = str(ok)
            elif isinstance(ok, str):
                ok = '"' + ok + '"'
            # print('adding ok:', ok)
            hasil.append(ok)
        if as_string:
            return ", ".join(hasil)
        return "[" + ", ".join(hasil) + "]"

    def fmus_run(self, program):
        from app.fmus import Fmus

        fmus = Fmus(env_int("ULIBPY_FMUS_DEBUG"))
        # fmus.set_file_dir_template(filepath)
        # fmus.set_file_template(filepath)
        # fmus.set_dir_template_from_file(filepath)
        fmus.process(program, capture_outerr=True)
        if "$*" in program:
            tidur(ms=env_int("ULIBPY_STDOUT_CAPTURE_SLEEP_MS"))
            if fmus.stdout or fmus.stderr:
                self.output = fmus.stdout if fmus.stdout else fmus.stderr

    def fmus_cmd(self, tree):
        """
        fmus_cmd
          fmus_execute  $*code /tmp
        fmus_cmd
          fmus_new
            fmus_new_basedir    /tmp/whatever
        fmus_cmd
          fmus_new
            fmus_new_filename   myfile.txt
        fmus_cmd
          fmus_new
            fmus_new_filepath   /tmp/hapus/myfile.txt
        """
        from editor import editor

        code = ""
        filepath = joiner(tempdir(), new_filename_timestamp())

        for item in anak(tree):
            if data(item) == "fmus_execute":
                code = token(item)
                program = code + "\n"
                # print('executing program:', program)
                self.fmus_run(program)
                # print('selesai')
            elif data(item) == "fmus_new":
                for basefile in anak(item):
                    if data(item) == "fmus_new_basedir":
                        basedir = token(item)
                        filepath = joiner(basedir, new_filename_timestamp())
                    elif data(item) == "fmus_new_filename":
                        filename = token(item)
                        filepath = joiner(tempdir(), filename)
                    elif data(item) == "fmus_new_filepath":
                        filepath = token(item)
                # pastikan filepath ada dan basedir terbuat
                program = editor(filepath)
                program = program + "\n"
                print("************")
                print(program)
                print("************")
                self.fmus_run(program)
        return filepath  # sementara...harusnya showtext/file utk coding

    def fmus_ops(self, tree):
        """
        fmus_ops
          fmus_keyword
          fmus_cmd
            fmus_execute  $*code /tmp
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "fmus_keyword":
                pass
            elif data(item) == "fmus_cmd":
                kembali += self.fmus_cmd(item)
        return kembali

    def redis_args(self, tree):
        """
        redis_args
          redis_arg
            redis_key   monyong
        """
        redis_arg = child1(tree)
        # kembali = ''
        args = []
        for item in anak(redis_arg):
            if data(item) == "redis_key":
                hasil = token(item)
                args.append(hasil)
            elif data(item) == "redis_value":
                # sementara value masih string
                # nanti bisa: dict, list, set
                hasil = token(item)
                args.append(hasil)

        kembali = args
        return kembali

    def redis_operation(self, tree):
        """ """
        from app.transpiler.zgenerate.helper.redis_helper import redis_process

        kembali = ""
        cmd, thing = "", ""
        args = []
        for item in anak(tree):
            if data(item) == "penanda":
                pass
            elif data(item) == "redis_string_get":
                cmd = "get"
            elif data(item) == "redis_string_add":
                cmd = "set"
            elif data(item) == "redis_keys":
                cmd = "list"
            elif data(item) == "redis_key":
                thing = token(item)
                args.append(thing)
            elif data(item) == "redis_value":
                thing = token(item)
                args.append(thing)
            elif data(item) == "redis_args":
                args = self.redis_args(item)

        hasil = redis_process(cmd, args)
        print(f"redis_process({cmd}, {args})", hasil)
        if isinstance(hasil, list):
            hasil = [item.decode("utf8") for item in hasil]
            print_enumerate(hasil)
            kembali = "\n".join(hasil)
        elif isinstance(hasil, str):
            kembali = hasil
        elif isinstance(hasil, bytes):
            kembali = hasil.decode("utf8")
        else:
            print("result:", type(hasil))
        return kembali

    def single_statement(self, jenisstmt, returning=True):
        """ """
        item = child1(jenisstmt)
        if item.data == "return_statement":
            output = self.return_statement(item, returning=returning)
            if returning:
                return output
        elif item.data == "var_declaration":
            output = self.var_declaration(item, returning=returning)
            if returning:
                return output
        elif item.data == "const_declaration":
            output = self.const_declaration(item, returning=returning)
            if returning:
                return output
        elif item.data == "assignment_statement":
            output = self.assignment_statement(item, returning=returning)
            if returning:
                return output
        elif item.data == "stdout_operation":
            hasil = self.stdout_operation(item)
            if returning:
                return hasil
            self.print(hasil)
        elif item.data == "typealias_declaration":
            hasil = self.typealias_declaration(item)
            if returning:
                return hasil
        elif item.data == "faker_ops":
            hasil = self.faker_ops(item)
            if returning:
                return hasil
            self.print(hasil)
        elif item.data == "fmus_ops":
            hasil = self.fmus_ops(item)
            if returning:
                return hasil
            self.print(hasil)
        elif item.data == "redis_operation":
            hasil = self.redis_operation(item)
            if returning:
                return hasil
            self.print(hasil)
        elif item.data == "dataops_statement_with_identifier":
            hasil = self.dataops_statement_with_identifier(item)
            if returning:
                return hasil
            self.print(hasil)

    def instantiation_expression(self, tree, returning=True):
        kembali = ""
        for item in anak(tree):
            if data(item) == "new_operator":
                pass
            elif data(item) == "nama_identifier":
                kembali += token(item)
            elif data(item) == "function_call_param":
                hasil = self.function_call_param(item, returning=returning)
                kembali += hasil
        if returning:
            return kembali
        self.print(kembali)

    def function_call_param(self, funcparam, add_self=False, returning=True):
        """
        function_param utk deklarasi/definisi fungsi
        function_call_param utk pemanggilan fungsi/method/constructor

        function_call_param
          callparamlist
            callparam
              literal
                literal_string        hello
        """
        if not beranak(funcparam):
            return "()"
        # callparamlist
        funcparamlist = funcparam.children[0]
        if funcparamlist.children:
            actualargs = []
            # print('iterate funcparamlist.children:', funcparamlist.children)
            for param in funcparamlist.children:
                # callparam
                # print('func call param:', param)
                # nama_identifier or named_values
                if not param.children:
                    """ """
                    continue
                namaid = param.children[0]
                if namaid.data == "nama_identifier":
                    # print('param nama_identifier')
                    argid = str(namaid.children[0])
                    actualargs.append(argid)
                elif namaid.data == "named_values":
                    """ """
                    # print('param named_values')
                    for kv in namaid.children:
                        # named_value = kv
                        namaidentifier = str(kv.children[0].children[0])
                        nilaiidentifier = kv.children[1]
                        ei = nilaiidentifier.children[0]
                        lit = ei.children[0]
                        nilaiidentifierstr = self.literal(lit)
                        actualargs.append(f"{namaidentifier}={nilaiidentifierstr}")
                elif namaid.data == "literal":
                    hasil = self.literal(namaid)
                    actualargs.append(hasil)

            the_params = ", ".join(actualargs)
            if add_self:
                if the_params:
                    the_params = "self, " + the_params
                else:
                    the_params = "self"
            result = f"({the_params})"
            if returning:
                return result
            self.output += result
        else:
            result = f'({"self" if add_self else ""})'
            if returning:
                return result
            self.output += result

    def for_start(self, tree):
        """
        for_start
          key_name  i
          expression_item
            literal
              literal_number        0
        """
        # keyname = token(child1(tree))
        # range_start_value = self.expression_item(child2(tree), returning=True)
        # return keyname, range_start_value
        keyname, range_start_value = "", ""
        for item in anak(tree):
            if data(item) == "nama_jenis_identifier_optional":
                keyname = self.nama_jenis_identifier_optional(item)
            elif data(item) == "expression_item":
                range_start_value = self.expression_item(item, returning=True)

        return keyname, range_start_value

    def for_end(self, forend):
        """
        for_end
          expression_item
            relational_expression
              expression_item
                nama_identifier     i
              operator_less
              expression_item
                literal
                  literal_number    5
        """
        # for (...; i<5; ...)
        # manual handle relational_expression
        ei = child1(forend)
        relation = child1(ei)
        kiri = child1(relation)
        kiri = self.expression_item(kiri, returning=True)
        # kiri gak penting
        oper = child2(relation)
        kanan = child3(relation)
        kanan = self.expression_item(kanan, returning=True)
        # sementara gak handle > dan >= utk for x in range(...; forend)
        print(
            f"forend, range oper: {oper}, end/kanan: {kanan}, type kanan: {type(kanan)}"
        )
        if data(oper) == "operator_less":
            return kanan
        elif data(oper) == "operator_less_equal":
            return kanan - 1
        return 0

    def for_while(self, tree):
        """
        go/for(i<10){?+i}
        go/for(){?+i}
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "expression_item":
                kembali += self.expression_item(item, returning=True)
        return kembali

    def for_ever(self, tree):
        """
        go/for(i<10){?+i}
        go/for(){?+i}
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "for_while":
                kembali += self.for_while(item)
        return kembali

    def for_traditional(self, tree):
        keyname, range_start, range_end, forstep = "", "", "", ""
        for item in anak(tree):
            if data(item) == "for_start":
                keyname, range_start = self.for_start(item)
            elif data(item) == "for_end":
                # range_end = self.for_end(item)
                ei = child1(item)
                range_end = self.expression_item(ei, returning=True)
            elif data(item) == "for_step":
                """
                for_step
                  expression_item
                    post_inc_expression
                      expression_item
                        nama_identifier     i
                """
                ei = child1(item)
                forstep = self.expression_item(ei, returning=True)

        if not forstep:
            # return f"{keyname} in range({range_start}, {range_end}):\n"
            return f"{keyname} := {range_start}; {range_end}"
        else:
            # return f"{keyname} in range({range_start}, {range_end}, {forstep}):\n"
            return f"{keyname} := {range_start}; {range_end}; {forstep}"

    def for_each(self, tree):
        """
        "@" for_each "@"  // for@item/items/index@
        for_each: item_name "/" array_name ("/" key_name)?
        for_each
          item_name   item
          array_name  items
        """
        index, value, items = "index", "", ""
        for item in anak(tree):
            if data(item) == "item_name":
                nama_jenis_identifier_optional = child1(item)
                value = self.nama_jenis_identifier_optional(
                    nama_jenis_identifier_optional
                )
            elif data(item) == "array_name":
                items = chtoken(item)
            elif data(item) == "key_name":
                nama_jenis_identifier_optional = child1(item)
                index = self.nama_jenis_identifier_optional(
                    nama_jenis_identifier_optional
                )

        # return f"{index}, {value} in enumerate({items})"
        return f"{index}, {value} := range {items}"

    def for_in(self, tree):
        """
        "#" for_in "#"    // for#key/items#
        for_in: key_name "/" array_name
        """
        index = token(child1(tree))
        items = token(child2(tree))
        return f"for (const {index} in {items}) {{" + "\n"

    def for_of(self, tree):
        thing, things = "", ""
        for item in anak(tree):
            if data(item) == "item_name":
                nama_jenis_identifier_optional = child1(item)
                thing = self.nama_jenis_identifier_optional(
                    nama_jenis_identifier_optional
                )
            elif data(item) == "array_name":
                for cucu in anak(item):
                    if data(cucu) == "nama_identifier":
                        things = chtoken(item)
                    elif data(cucu) == "expression_item":
                        things = self.expression_item(cucu)
        return f"(const {thing} of {things})"

    def for_variation(self, tree):
        """
        returning value instead of self.output += ...

        for_variation
          for_traditional
          for_each = for k,v
          for_in = for_key
          for_of = for_value

        for index,item in enumerate(items): ...
        -> index,item in enumerate(items): ...
        """
        varian = child1(tree)
        if data(varian) == "for_traditional":
            # hasil = self.for_traditional(varian)
            # self.output += hasil
            return self.for_traditional(varian)
        elif data(varian) == "for_each":
            return self.for_each(varian)
        elif data(varian) == "for_in":
            return self.for_in(varian)
        elif data(varian) == "for_of":
            return self.for_of(varian)
        elif data(varian) == "for_ever":
            return self.for_ever(varian)
        return ""

    def condition_for(self, tree):
        """
        returning value instead of self.output += ...

        condition_for
          expression_item
            literal
              literal_number      42
        condition_for
          for_variation
        """
        ei = child1(tree)
        if data(ei) == "expression_item":
            return self.expression_item(ei, returning=True)
        elif data(ei) == "for_variation":
            return self.for_variation(ei)

        return ""

    def condition_body(self, tree, returning=True):
        """
        condition_body
          statement_list
        """
        if beranak(tree):
            sl = child1(tree)
            output = self.statement_list(sl, returning=returning)
            if returning:
                return output
        else:
            """
            for@item/items@{}

            utk empty for
            asumsikan ini berlaku utk selain for: switch dll
            """
            # if data(bapak(tree)) == 'for_statement':
            #   '''
            #   sudah ada "for" tambah ":\n"
            #   '''
            kembali = "{}"
            if returning:
                return kembali
            self.print(kembali)

    def for_statement(self, tree, returning=True):
        kembali, forname, forcondition, forbody = "", "", "", ""
        for item in anak(tree):
            if data(item) == "for_keyword":
                forname = "for"
            elif data(item) == "condition_for":
                forcondition = self.condition_for(item)
            elif data(item) == "condition_body":
                self.inc()
                forbody = self.condition_body(item, returning=True)
                print("peroleh for body", forbody)
                self.dec()
        # forbody termasuk ':', no space dg condition
        # kembali = f'{forname} {forcondition} {forbody}'
        if not forcondition:
            kembali += f"{forname}"
        else:
            kembali += f"{forname} {forcondition}"
        kembali += " {\n"
        # TODO: tabify content
        # kembali += forbody
        # kembali += tabify_content_tab(forbody, num_tab=1, delim='\n')
        kembali += tabify_content_space(forbody, num_tab=1, delim="\n")
        kembali += "\n}"
        # if returning:
        #   return kembali
        # self.print(kembali)
        return kembali

    def if_statement(self, tree, returning=True):
        """
        if_statement
          if_keyword
          condition_then_if
            condition_if
              expression_item
                literal
                  literal_number    42
            condition_body
              statement_list
                statement_item
                  expression_item
                    literal
                      literal_string        ini if
        if (if)/elif/ /elif/(else)
        """
        ifkeyword = child1(tree)
        kembali = ""  # digunakan hanya jk returning
        self.inc()
        condition_then_if = child2(tree)
        condition_if = child1(condition_then_if)
        condition_body = child2(condition_then_if)
        if data(condition_if) == "condition_if":
            ei = child1(condition_if)
            kembalikan_ekspresi = self.expression_item(ei, returning=True)
            if returning:
                kembali += f"if {kembalikan_ekspresi}:\n"
            else:
                self.output += f"if {kembalikan_ekspresi}:\n"

        output = self.condition_body(condition_body, returning=returning)
        self.dec()  # kurangi indent dulu
        if returning:
            return kembali + output

    def condition_while(self, condition_while):
        """
        condition_while
          expression_item
            relational_expression
              expression_item
                nama_identifier   i
              operator_less
              expression_item
                literal
                  literal_number  2
        """
        ei = child1(condition_while)
        hasil = self.expression_item(ei, returning=True)
        return hasil

    def while_statement(self, tree, returning=True):
        """
        while_statement
          while_keyword
          condition_while
          condition_body
            statement_list
              statement_item
                expression_item
                  function_call
                    function_name   print
                    argument_list
                      argument
                        expression_item
                          literal
                            literal_string  Hello
              statement_separator
              statement_item
                expression_item
                  function_call
                    function_name   print
        """
        whilekw = child1(tree)
        condition_while = child2(tree)
        hasil = self.condition_while(condition_while)
        if returning:
            kembali = f"while {hasil}:\n"
        else:
            self.output += f"while {hasil}:\n"
        self.inc()
        condition_body = child3(tree)
        output = self.condition_body(condition_body, returning=returning)
        self.dec()
        if returning:
            return kembali + output

    def condition_switch(self, tree):
        """
        condition_switch
          expression_item
            nama_identifier       myvalue
        """
        ei = child1(tree)
        hasil = self.expression_item(ei, returning=True)
        return hasil

    def case_body(self, tree, terbanding, first_case=False, returning=True):
        """
        first_case => if, otherwise: elif
        case_body

          condition_case
            expression_item
              literal
                literal_number    42
          -- or
          condition_defaultcase

          condition_body
            statement_list
              statement_item
                expression_item
                  function_call
                    function_name print
                    argument_list
                      argument
                        expression_item
                          literal
                            literal_string        asyik
        s(myvalue)(42){print("asyik")}(43){print("dapat 43")}(){print("default")}
        """
        condition_case = child1(tree)

        if data(condition_case) == "condition_defaultcase":
            # elif_keyword = 'default'
            header = f"else:\n"
        elif data(condition_case) == "condition_case":
            # elif_keyword = 'elif'
            if_or_elif = "if" if first_case else "elif"
            ei = child1(condition_case)
            membanding = self.expression_item(ei, returning=True)
            header = f"{if_or_elif} {terbanding} == {membanding}:\n"

        if returning:
            kembali = header
        else:
            self.output += header
        condition_body = child2(tree)
        statement_list = child1(condition_body)
        self.inc()
        output = self.statement_list(statement_list, returning=returning)
        self.dec()

        if returning:
            return kembali + output + "\n"

        self.output += "\n"  # agar elif dan else mulai dari newline

    def switch_statement(self, tree, returning=True):
        """
        s(myvalue)(42){print("asyik")}(43){print("dapat 43")}
        """
        swkw = child1(tree)
        terbanding = None
        # condition_switch = child2(tree)
        # if terbanding == nilai ... elif terbanding == nilai ... else ...
        # terbanding = self.condition_switch(condition_switch)
        # case_body = child3(tree)
        # self.case_body(case_body, terbanding)

        kembali = ""  # dipake utk returning

        first_case = True
        for cond_or_case in anak(tree):
            if data(cond_or_case) == "condition_switch":
                terbanding = self.condition_switch(cond_or_case)
                # print('terbanding adlh', terbanding)
            elif data(cond_or_case) == "case_body":
                kembali += self.case_body(
                    cond_or_case, terbanding, first_case, returning=returning
                )
                if first_case:
                    first_case = False

        if returning:
            return kembali

    def statement_item(self, contentitem, within_statement_list=False):
        """ """
        jenisstmt = child1(contentitem)
        if jenisstmt.data == "single_statement":
            output = self.single_statement(jenisstmt, returning=True)
            if within_statement_list:
                return output
            self.print(output)
        elif jenisstmt.data == "instantiation_expression":
            output = self.instantiation_expression(jenisstmt, returning=True)
            if within_statement_list:
                return output
            self.print(output)
        elif jenisstmt.data == "for_statement":
            output = self.for_statement(jenisstmt, returning=True)
            if within_statement_list:
                return output
            self.print(output)
        elif jenisstmt.data == "if_statement":
            output = self.if_statement(jenisstmt, returning=True)
            if within_statement_list:
                return output
            self.print(output)
        elif jenisstmt.data == "expression_item":
            output = self.expression_item(jenisstmt, returning=True)
            if within_statement_list:
                return output
            self.print(output)
        elif jenisstmt.data == "while_statement":
            output = self.while_statement(jenisstmt, returning=True)
            if within_statement_list:
                return output
            self.print(output)
        elif jenisstmt.data == "switch_statement":
            output = self.switch_statement(jenisstmt, returning=True)
            if within_statement_list:
                return output
            self.print(output)
        elif jenisstmt.data == "enum_declaration":
            output = self.enum_declaration(jenisstmt)
            if within_statement_list:
                return output
            self.print(output)

    def statement_list(self, tree, returning=True):
        """
        statement_list
          statement_item
            expression_item
              literal
                literal_string  hello
          statement_separator
          statement_item
            if_statement
              if_keyword
              condition_then_if
                condition_if
                  expression_item
                    literal
                      literal_number    42
                condition_body
                  statement_list
                    statement_item
                      expression_item
                        literal
                          literal_string        ini if
        """
        for stmt in anak(tree):
            if data(stmt) == "statement_item":
                output = self.statement_item(stmt, within_statement_list=True)
                # if output:
                #   output = output + ';'
                if returning:
                    return output
                self.print(output)
            elif data(stmt) == "statement_separator":
                if returning:
                    return "\n"
                self.print("\n")

    def functioncontent(self, tree):
        """
        functioncontent
          statement_item
            expression_item
              arithmetic_expression
                expression_item
                  arithmetic_expression
                    expression_item
                      nama_identifier a
                    operator_plus
                    expression_item
                      nama_identifier b
                operator_mult
                expression_item
                  literal
                    literal_number    10
        """
        # print('func content:', tree)
        direct_child = child1(tree)
        if data(direct_child) == "statement_item":
            hasil = self.statement_item(direct_child, returning=True)
            # print('hasil statement item:', statement_item)
            return hasil

    def functioncontentlist(self, tree):
        """
        functioncontentlist
          functioncontent
            statement_item
              expression_item
                arithmetic_expression
                  expression_item
                    arithmetic_expression
                      expression_item
                        nama_identifier a
                      operator_plus
                      expression_item
                        nama_identifier b
                  operator_mult
                  expression_item
                    literal
                      literal_number    10
        """
        allcontent = []
        for item in anak(tree):
            hasil = self.functioncontent(item)
            if hasil:
                allcontent.append(hasil)
        # print('allcontent sblm ditabify', allcontent)
        tabify = [self.tab() + item for item in allcontent]
        pemisah_content = "\n"
        return pemisah_content.join(tabify)

    def function_content(self, funccontent, returning=True):
        """
        foo(){}
        function_item
          function_name     foo
          function_param
          function_content

          function_content
            functioncontentlist
              functioncontent
                statement_item
                  expression_item
                    arithmetic_expression
                      expression_item
                        arithmetic_expression
                          expression_item
                            nama_identifier a
                          operator_plus
                          expression_item
                            nama_identifier b
                      operator_mult
                      expression_item
                        literal
                          literal_number    10
        """
        kembali = ""
        if beranak(funccontent):
            # functioncontentlist
            functioncontentlist = child1(funccontent)
            hasil = self.functioncontentlist(functioncontentlist)
            if hasil:
                return hasil
            else:
                if returning:
                    return kembali + f"\n{self.tab()}// pass\n"
                else:
                    # f(){} empty funcbody
                    self.print(f"\n{self.tab()}// pass\n")
        else:
            if returning:
                return kembali + f"\n{self.tab()}// pass\n"
            else:
                self.print(f"\n{self.tab()}// pass\n")

    def nama_jenis_identifier_array(self, tree):
        """
        array
          item_type
            integer
        """
        kembalian = "__JENIS[]"
        if beranak(tree):
            prim = child1(tree)  # item_type
            primi = child1(prim)  # integer
            primitive = data(primi)
            petakan = peta_tipe_data.get(primitive, primitive)
            kembalian = kembalian.replace("__JENIS", petakan)
            return kembalian
        kembalian = kembalian.replace("__JENIS", "")
        return kembalian

    def nama_jenis_identifier(self, tree):
        """
        nama_jenis_identifier
          nama_identifier   array
          tipe_identifier
            array
              item_type
                integer
        nama_jenis_identifier
          nama_identifier   satu
          tipe_identifier
            string
        number[]
        """
        nama = child1(tree)
        namaid = token(nama)
        jenis = child2(tree)
        primitive_or_collection = child1(jenis)
        # ini baru array, belum collection lain
        if data(primitive_or_collection) == "array":
            hasil = self.nama_jenis_identifier_array(primitive_or_collection)
            return f"{namaid}: {hasil}"
        else:
            jenis = data(primitive_or_collection)
            tipenative = peta_tipe_data.get(jenis, jenis)
            return f"{namaid} {tipenative}"

    def function_param(self, funcparam, add_self=False, returning=True):
        """
        utk method/ctor: add_self=True
        utk function call, class instantiation (memanggil ctor): function_call=True

        standalone spt ini gak punya anak
        function_param
        """
        # end_with_colon = "" if function_call else ":"

        if beranak(funcparam):
            # paramlist
            funcparamlist = child1(funcparam)
            actualargs = self.paramlist(funcparamlist)
            the_params = ", ".join(actualargs)
            if returning:
                return f"({the_params})"
            else:
                self.output += f"({the_params})"
        else:
            if returning:
                return f'({"self" if add_self else ""})'
            else:
                self.output += f'({"self" if add_self else ""})'

    def anon_expression(self, tree):
        """
        anon_expression
          expression_item
            arithmetic_expression
              expression_item
                nama_identifier   x
              operator_mult
              expression_item
                literal
                  literal_number  2
        """
        return self.expression_item(child1(tree), returning=True)

    def anon_statements(self, tree):
        """
        returning by default True krn kita pengen apit ini dg {}

        anon_statements
          statement_item
            single_statement
              return_statement
                expression_item
                  arithmetic_expression
                    expression_item
                      nama_identifier     x
                    operator_mult
                    expression_item
                      literal
                        literal_number    2
        di sini sengaja kembalikan list
        agar pemanggil tau apa hrs gunakan {} atau tidak
        jk hanya ada 1 statement maka tidak perlu {}
        jk 0 atau lebih dari 1 maka gunakan {} utk mengapit
        """
        statement_list = []
        # statement_item = child1(tree)
        # hasil = self.statement_item(statement_item, returning=True)
        for statement in anak(tree):
            # print('statement x:', statement.pretty())
            if data(statement) == "statement_item":
                # skip statement_separator
                hasil = self.statement_item(statement, returning=True)
                hasil = str(hasil)  # si -> ei -> suka hasilkan number
                statement_list.append(hasil)

        # print('peroleh statement_list:', statement_list)
        return statement_list

    def anonymous_function(self, tree):
        """
        argument
          anonymous_function
            non_arrow_func
              keyword_function
            function_param
              paramlist
                param
                  nama_identifier     x
            anon_expression
              ...
            * atau
            anon_statements
              ...
        non_arrow_func + function_param + anon_expression|anon_statements
        """
        # harus ada mode: arrow func atau normal func
        # default adlh arrow func
        # print('oprek anon func utk', tree.pretty())
        # arrow_func_mode = True
        # arrow_uses_expression = True
        kembali = ""
        if jumlahanak(tree) == 3:  # normal func -> :(){42}
            # oprek_config = child1(tree)
            # arrow_func_mode = False
            oprek_param = child2(tree)
            # print('anon func: normal func, oprek_param:', oprek_param)
            params = self.function_param(oprek_param, returning=True)
            # print('anon func: normal func, params:', params)
            oprek_body = child3(tree)
            if data(oprek_body) == "anon_expression":
                hasil = self.anon_expression(oprek_body)
                # print('found expr:', hasil)
                # self.print(f'function {params} {{\n')
                # self.print(self.tab() + hasil)
                # self.print('\n}')
                kembali += f"function {params} {{" + hasil + "\n}"
            elif data(oprek_body) == "anon_statements":
                # self.print(f'function {params} {{')
                self.inc()
                badan_fungsi = self.anon_statements(oprek_body)
                badan_fungsi = [self.tab() + item + ";" for item in badan_fungsi]
                badan_fungsi = "\n".join(badan_fungsi)
                self.dec()
                kembali += f"function {params} {{\n" + badan_fungsi + "\n}"
        else:
            # default/arrow func, gak perlu {} utk anon expr dan anon stats yg cuma 1 child
            # print('sblm function_param, child anon func #1')
            oprek_param = child1(tree)
            params = self.function_param(oprek_param, returning=True)
            # print('sblm body anon expr/stmt, child anon func #2')
            oprek_body = child2(tree)
            if data(oprek_body) == "anon_expression":
                # print('hajar anon expressions')
                hasil = self.anon_expression(oprek_body)
                # self.print(f'{params} => {hasil}')
                kembali += f"{params} => {hasil}"
            elif data(oprek_body) == "anon_statements":
                """
                arrow.map(42, (x){x*2; y*5})
                """
                # print('hajar anon statements')
                # self.print(f'{params} => {{')
                badan_fungsi = self.anon_statements(oprek_body)
                # print('badan_fungsi:', badan_fungsi)
                # cek jumlah statement dlm badan_fungsi
                if len(badan_fungsi) == 1:
                    konten = badan_fungsi[0]
                else:
                    # mungkin perlu self.tab() stlh \n
                    # yup, bahkan perlu ;
                    self.inc()  # berlaku sblm panggil self.tab()
                    badan_fungsi = [self.tab() + item + ";" for item in badan_fungsi]
                    transform = "\n".join(badan_fungsi)
                    self.dec()
                    konten = "{\n" + transform + "\n}"
                kembali += f"{params} => " + konten

        return kembali

    def named_value(self, tree):
        """
        named_value
          nama_identifier   username
          tipe_identifier
            string
          nilai_identifier
            expression_item
              literal
                literal_string      wieke
        """
        nama, jenis, nilai = "", "", ""
        for item in anak(tree):
            if data(item) == "nama_identifier":
                nama = token(item)
            elif data(item) == "tipe_identifier":
                # jenis = chdata(item) # python gak pake type sementara
                jenis = self.tipe_identifier(item)
            elif data(item) == "nilai_identifier":
                ei = child1(item)
                nilai = self.expression_item(ei, returning=True)
        return nama, jenis, nilai

    def named_values(self, tree):
        """
        named_values
          named_value
            nama_identifier   username
            tipe_identifier
              string
            nilai_identifier
              expression_item
                literal
                  literal_string      wieke

        # print('param named_values')
        for kv in namaid.children:
          # named_value = kv
          namaidentifier = str(kv.children[0].children[0])
          nilaiidentifier = kv.children[1]
          ei = nilaiidentifier.children[0]
          lit = ei.children[0]
          nilaiidentifierstr = self.literal(lit)
        actualargs.append(f'{namaidentifier}={nilaiidentifierstr}')
        """
        # username=some,password=some
        args = []
        for nv in anak(tree):
            if data(nv) == "named_value":
                nama, jenis, nilai = self.named_value(nv)
                if jenis:
                    args.append(f"{nama}: {jenis} = {nilai}")
                else:
                    args.append(f"{nama}={nilai}")
        return ", ".join(args)

    def argument_list(self, tree):
        """
        argument_list
          argument
            named_values
              named_value
                nama_identifier   username
                tipe_identifier
                  string
                nilai_identifier
                  expression_item
                    literal
                      literal_string      wieke
        """
        args = []
        for arg in anak(tree):
            # argument
            for tipearg in anak(arg):
                if data(tipearg) == "named_values":
                    # print('named_values #1')
                    hasil = self.named_values(tipearg)
                    # print('named_values #2', hasil)
                    args.append(hasil)
                elif data(tipearg) == "expression_item":
                    hasil = self.expression_item(tipearg, returning=True)
                    hasil = str(hasil)
                    args.append(hasil)
                elif data(tipearg) == "anonymous_function":
                    hasil = self.anonymous_function(tipearg)
                    args.append(hasil)

        # kembalikan list
        return args

    def function_call(self, tree):
        """ """
        functionname, callparams = "", "()"
        for item in anak(tree):
            if data(item) == "function_name":
                funcname = item  # child1(tree)
                # funcname mesti beranak, apakah nama atau tree
                anak_nama_fungsi = child1(funcname)
                if istoken(anak_nama_fungsi):
                    functionname = token(funcname)
                elif data(anak_nama_fungsi) == "nama_identifier_with_typeparams":
                    functionname = self.nama_identifier_with_typeparams(
                        anak_nama_fungsi
                    )
            elif data(item) == "argument_list":
                argument_list = item  # child2(tree)
                args = self.argument_list(argument_list)
                callparams = f'({", ".join(args)})'

        return self.tab() + f"{functionname}{callparams}"

    def function_name(self, tree):
        """
        function_name
          nama_identifier_with_typeparams
            nama_identifier       myfunc
        function_name: nama_identifier_with_typeparams
        """
        nama_identifier_with_typeparams = child1(tree)
        name = self.nama_identifier_with_typeparams(nama_identifier_with_typeparams)
        return name

    def function_item(self, cucu, returning=True):
        kembali = ""
        tipe_kembali = ""
        for item in anak(cucu):
            if data(item) == "keyword_function":
                pass
            elif data(item) == "function_name":
                name = self.function_name(item)
                kembali += "func " + name
            elif data(item) == "tipe_identifier":
                tipe_kembali = self.tipe_identifier(item)
            elif data(item) == "function_param":
                param = self.function_param(item, returning=True)
                kembali += param
                if tipe_kembali:
                    kembali += f" {tipe_kembali}"
            elif data(item) == "function_content":
                self.inc()
                content = self.function_content(item, returning=True)
                kembali += " {\n" + content
                self.dec()
                kembali += "\n}"

        if returning:
            return kembali

        self.print(kembali)

    def constructor_content(self, ctor_method_field):
        """ """
        kembali = f"\n{self.tab()}constructor "
        # self.output +=
        self.inc()
        # function_param
        ctorparam = child1(ctor_method_field)
        kembali += self.function_param(ctorparam, returning=True)

        kembali += " {"
        # function_content
        ctorcontent = child2(ctor_method_field)
        kembali += self.function_content(ctorcontent, returning=True)
        # kembali += self.tab() + "}" # tab dulu krn kita ctor dlm class
        kembali += "}"  # tab dulu krn kita ctor dlm class
        self.dec()
        return kembali

    def method_content(self, tree):
        """ """
        kembali = ""
        tipe_identifier = ""
        methodname, methodtype, methodparam, methodcontent = "", "", "", ""
        for item in anak(tree):
            if data(item) == "function_name":
                nama_identifier_with_typeparams = child1(item)
                methodname = self.nama_identifier_with_typeparams(
                    nama_identifier_with_typeparams
                )
                # kembali += f'{nama}'
            elif data(item) == "tipe_identifier":
                methodtype = self.tipe_identifier(item)
            elif data(item) == "function_param":
                methodparam = self.function_param(item, returning=True)
            elif data(item) == "function_content":
                # kembali += ' {\n'
                # self.inc()
                methodcontent = self.function_content(item, returning=True)
                # kembali += '\n'
                # self.dec()
                # kembali += self.tab() + '}'

        if self.track_methods_for_interface:
            kembali = f"{methodname}{methodparam} {methodtype}"
        else:
            kembali = (
                f"func {methodname}{methodparam} {methodtype} {{ {methodcontent} }}"
            )
        if self.track_methods_for_interface:
            self.track_methods.append(kembali)
        return kembali

    def go_initialize_field(self, structname, fieldname, fieldtype, nilai):
        """
        https://stackoverflow.com/questions/19650265/is-there-a-faster-shorter-way-to-initialize-variables-in-a-rust-struct
        impl Default for structname {
          fn default() -> structname {
            structname {
              fieldname: nilai,
            }
          }
        }
        """
        from .common import go_struct_template

        hasil = (
            go_struct_template.replace("__structname^", structname.capitalize())
            .replace("__structname", structname)
            .replace("__fieldname", fieldname)
            .replace("__fieldtype", fieldtype)
            .replace("__nilai", nilai)
        )
        return hasil

    def field_content(self, tree, structname=None):
        """
        field_content
          field_name        username
          tipe_identifier
            string
          declaration_value
            expression_item
              literal
                literal_string      usef
        field_content:
          field_config?
          field_name
          tipe_identifier?
          declaration_value?
        """
        field_name, field_type = "", "string"  # default field type = string
        kembali_struct, kembali_impl = "", ""
        for item in anak(tree):
            if data(item) == "field_config":
                pass
            elif data(item) == "field_name":
                field_name = token(item)
                kembali_struct += field_name
            elif data(item) == "tipe_identifier":
                field_type = self.tipe_identifier(item)
                kembali_struct += f": {field_type}"
            elif data(item) == "declaration_value":
                nilai = self.declaration_value(item)
                kembali_impl = self.go_initialize_field(
                    structname, field_name, field_type, nilai
                )

        # kembali_struct += ';'
        return kembali_struct, kembali_impl

    def classcontent(self, tree, structname=None):
        """
        class_content -> classcontentlist -> classcontent
        classcontentlist
          classcontent
            method_content
              function_name
                nama_identifier_with_typeparams
                  nama_identifier       len
              function_param
              function_content
          classcontent
            constructor_content
              function_param
                paramlist
                  param
              function_content
                functioncontentlist
                  functioncontent
        """
        if not beranak(tree):
            return None, ""
        # constructor_content
        ctor_method_field = child1(tree)
        field_impl = ""
        if ctor_method_field.data == "constructor_content":
            item = self.constructor_content(ctor_method_field)
            return item, field_impl
        elif data(ctor_method_field) == "method_content":
            item = self.method_content(ctor_method_field)
            return item, field_impl
        elif data(ctor_method_field) == "field_content":
            item, field_impl = self.field_content(
                ctor_method_field, structname=structname
            )
            return item, field_impl

    def classcontentlist(self, tree, structname=None):
        """
        class_content -> classcontentlist -> classcontent
        classcontentlist
          classcontent
          classcontent
        """
        collected_content = []
        field_name_impl = {}
        for classcontent in anak(tree):
            hasil, field_impl = self.classcontent(classcontent, structname=structname)
            field_name_impl[hasil] = field_impl
            if hasil:
                collected_content.append(hasil)
        if collected_content:
            tabbed_class_contents = [self.tab() + item for item in collected_content]
            tabbed_class_contents = "\n".join(tabbed_class_contents)
            kembali = "{\n" + tabbed_class_contents + "\n}"
        else:
            # no content jadi {} utk ts dan pass utk python
            # self.print('{}')
            kembali = "{}"

        return kembali, field_name_impl

    def class_config(self, tree):
        """ """
        classconfiglist = child1(tree)
        semua_modifier = []
        prepender, appender = "", ""
        for nilai in anak(classconfiglist):
            # print('oprek nilai:', nilai)
            if data(nilai) == "public":
                hasil = "public"
                semua_modifier.append(hasil)
            elif data(nilai) == "private":
                hasil = "private"
                semua_modifier.append(hasil)
            elif data(nilai) == "protected":
                hasil = "protected"
                semua_modifier.append(hasil)
            elif data(nilai) == "static":
                hasil = "static"
                semua_modifier.append(hasil)
            elif data(nilai) == "abstract":
                hasil = "abstract"
                semua_modifier.append(hasil)
            elif data(nilai) == "async":
                hasil = "async"
                semua_modifier.append(hasil)
            elif data(nilai) == "extends":
                """
                extends
                  nama_identifier     Sports
                """
                appender = "extends " + chtoken(nilai)

        if semua_modifier:
            prepender = " ".join(semua_modifier)
            return prepender, appender
        return prepender, appender

    def class_content(self, tree, structname=None):
        """
        class_content -> classcontentlist -> classcontent
        class_content
          classcontentlist
            classcontent
              method_content
                function_name
                  nama_identifier_with_typeparams
                    nama_identifier       len
                function_param
                function_content
        """
        # classcontentlist
        if not beranak(tree):
            return None, ""
        classcontentlist = child1(tree)
        kembali, field_name_impl = "", ""
        if beranak(classcontentlist):
            hasil, field_name_impl = self.classcontentlist(
                classcontentlist, structname=structname
            )
            kembali = hasil

        # do something if we have content
        # if not collected_content:
        else:
            kembali = "{}"

        return kembali, field_name_impl

    def paramlist(self, tree):
        """
        function_param
          paramlist <- tree
            param
              nama_identifier     satu
        paramlist
          param
            nama_jenis_identifier
              nama_identifier   satu
              tipe_identifier
                string
        """
        all_params = []
        for param in anak(tree):
            if not beranak(param):
                continue

            paramname_dan_tipe = ""
            paramchild = child1(param)

            if data(paramchild) == "nama_identifier":
                paramname_dan_tipe = chtoken(param)
            elif data(paramchild) == "named_values":
                paramname_dan_tipe = self.named_values(paramchild)
            elif data(paramchild) == "nama_jenis_identifier":
                tipe_data = self.nama_jenis_identifier(paramchild)
                paramname_dan_tipe = tipe_data

            if paramname_dan_tipe:
                # print('param name+tipe:', paramname_dan_tipe)
                all_params.append(paramname_dan_tipe)
        return all_params

    def type_parameter_list(self, tree):
        all_params = []
        for param in anak(tree):
            if data(param) == "type_parameter" and chdata(param) == "nama_identifier":
                paramname = chtoken(param)
                all_params.append(paramname)
        return all_params

    def type_parameters(self, tree):
        """
        type_parameters <- ada ini
          type_parameter_list
            type_parameter
              nama_identifier T
        """
        # type_parameters = child2(nama_identifier_with_typeparams)
        # param_jenis = self.type_parameters(type_parameters)
        paramlist = child1(tree)
        all_params = self.type_parameter_list(paramlist)
        return "<" + ", ".join(all_params) + ">"

    def nama_identifier_with_typeparams(self, tree):
        """
        nama_identifier_with_typeparams
          nama_identifier       a
          type_parameters
            type_parameter_list
              type_parameter
                nama_identifier T
        """
        nama_identifier = child1(tree)
        # print('tree adlh', data(tree))
        if sebanyak(tree, 2):
            """
            nama_identifier_with_typeparams
              nama_identifier       a             <- tree child 1
              type_parameters                     <- tree child 2
                type_parameter_list
                  type_parameter
                    nama_identifier T
            """
            # print('beranak 2 #1')
            type_parameters = child2(tree)
            param_jenis = self.type_parameters(type_parameters)
            # print(f'beranak 2 #2: {param_jenis}')
            class_namestr = token(nama_identifier) + param_jenis
        else:
            """
            nama_identifier_with_typeparams
              nama_identifier       a
            """
            class_namestr = chtoken(tree)

        return class_namestr

    def class_item(self, cucu):
        """
        class_item
          class_name
            nama_identifier_with_typeparams
              nama_identifier       a
              type_parameters
                type_parameter_list
                  type_parameter
                    nama_identifier T
          class_content
            classcontentlist
              classcontent
        class_item
          class_name
            nama_identifier_with_typeparams
              nama_identifier       my
          class_content
            classcontentlist
              classcontent
        """
        self.inc()
        # class_name
        class_name = child1(cucu)
        class_namestr = ""
        if chdata(class_name) == "nama_identifier_with_typeparams":
            # print('#1 class_item -> nama_identifier_with_typeparams')
            nama_identifier_with_typeparams = child(class_name)
            # print(f'#2 class_item -> {nama_identifier_with_typeparams}')
            class_namestr = self.nama_identifier_with_typeparams(
                nama_identifier_with_typeparams
            )
            # print(f'#3 class_item -> class_namestr = {class_namestr}')
        elif chdata(class_name) == "nama_identifier":
            class_namestr = token(class_name)
        self.print(f"type {class_namestr} struct ")
        # class_content
        class_content = child2(cucu)
        hasil, field_name_impl = self.class_content(
            class_content, structname=class_namestr
        )
        self.print(hasil)
        if field_name_impl:
            self.print("\n")
            for k, v in field_name_impl.items():
                self.print(v)
        self.dec()

    def class_name(self, tree):
        """
        class_name
          nama_identifier_with_typeparams
            nama_identifier       a
            type_parameters
              type_parameter_list
                type_parameter
                  nama_identifier T
        """
        # if chdata(item) == 'nama_identifier_with_typeparams':
        nama_identifier_with_typeparams = child(tree)
        namakelas = self.nama_identifier_with_typeparams(
            nama_identifier_with_typeparams
        )
        return namakelas

    def create_module_and_class(self, ifacename, ifacecontent):
        """ """
        kembali = f"type {ifacename} interface"
        self.inc()
        kembali += self.tabify_content(ifacecontent)
        self.dec()

        pengguna = ifacename + "Implementor"
        huruf = pengguna[0]

        kembali += "\n" * 3
        kembali += f"type {pengguna} struct {{}}"
        kembali += "\n" * 3

        # self.inc()
        # kembali += f'func ({huruf} {pengguna}) for {pengguna}'
        # # kembali += self.tabify_content(ifacecontent)
        # self.dec()
        for item in self.track_methods:
            kembali += f"func ({huruf} {pengguna}) {item} {{\n}}\n"
        return kembali

    def interface_item(self, tree):
        """
        interface_item
          interface_keyword
          class_name
            nama_identifier_with_typeparams
              nama_identifier       myinterafce
          class_content
            classcontentlist
              classcontent
        """
        kembali = ""
        prepender, appender = "", ""
        ifacename, ifaceconfig, ifacecontent = "", "", ""
        for item in anak(tree):
            if data(item) == "interface_keyword":
                pass
            elif data(item) == "class_name":
                ifacename = self.class_name(item)
            elif data(item) == "class_config":
                prepender, appender = self.class_config(item)
                print("appender dan prepender utk iface:", prepender, "&", appender)
                ifaceconfig = prepender + " "
            elif data(item) == "class_content":
                ifacecontent, field_name_impl = self.class_content(item, ifacename)
        kembali = self.create_module_and_class(ifacename, ifacecontent)
        return kembali

    def block_item(self, tree):
        kembali = ""
        for cucu in anak(tree):
            if cucu.data == "function_item":
                kembali += self.function_item(cucu)
            elif cucu.data == "class_item":
                kembali += self.class_item(cucu)
            elif cucu.data == "interface_item":
                try:
                    self.track_methods_for_interface = True
                    kembali += self.interface_item(cucu)
                    # self.print(could_be_none)
                    print("self.track_methods:", self.track_methods)
                    self.track_methods_for_interface = False
                    self.track_methods = []
                except Exception as err:
                    print(traceback.format_exc())
        if kembali:
            self.print(kembali)

    def import_things(self, tree):
        """
        import_things
          import_thing_default      aposerver
          import_thing_default      apocore
        import_things
          import_thing_enclose      <- gak ada efek utk python
            import_thing_default    sys
        """
        imports = []
        for item in anak(tree):
            if data(item) == "import_thing_default":
                imports.append(token(item))
            elif data(item) == "import_thing_enclose":
                ambil = "{ " + chtoken(item) + " }"
                imports.append(ambil)
        return ", ".join(imports)

    def search_term(self, terms, filepath):
        """ """
        from app.greputils import pattern_search

        hasil = pattern_search(filepath, terms)
        return hasil

    def searchable(self, tree, filepath="data/import_go.txt"):
        """
        searchable
          searchable_kw
          search_term       carilah karena kamu dicari
          searchable_kw
        """
        hasil = ""
        for item in anak(tree):
            if data(item) == "search_term":
                terms = token(item).strip().split()
                # print('searching:', terms)
                hasil = self.search_term(terms, filepath)
        return hasil

    def import_item(self, tree):
        """
        I/sys
        import_item
          keyword_import
          import_things
            import_thing_enclose      <- gak ada efek utk python
              import_thing_default    sys
        Isys
        import_item
          keyword_import
          import_things
            import_thing_default      sys

        Itreesitter|language,parser
        import_item
          keyword_import
          import_container    treesitter
          import_things
            import_thing_default      language
            import_thing_default      parser
        """
        container = None
        merged_imports = []
        search_mode = False
        for item in anak(tree):
            if data(item) == "import_container":
                container = token(item)
            # elif data(kw_cont_thing) == 'import_things':
            #   default_or_enclose = child1(kw_cont_thing)
            #   if data(default_or_enclose) == 'import_thing_enclose':
            #     thing = child1(default_or_enclose)
            #     item = token(thing)
            #     merged_imports.append(item)
            #   elif data(default_or_enclose) == 'import_thing_default':
            #     item = token(default_or_enclose)
            #     merged_imports.append(item)
            elif data(item) == "import_things":
                hasil = self.import_things(item)
                merged_imports.append(hasil)
            elif data(item) == "searchable":
                search_mode = True
                filepath = joiner(here(__file__), "../data/import_go.txt")
                from app.dirutils import normy

                filepath = normy(filepath)
                # print('filepath:', filepath)
                hasil = self.searchable(item, filepath)
                # print('hasil:', hasil)

        if search_mode:
            pass  # hasil sudah berisi yg diminta
        else:
            if container:
                hasil = f'from {container} import {", ".join(merged_imports)}'
            else:
                hasil = f'import {", ".join(merged_imports)}'

        self.output += hasil

    def package_things(self, tree):
        kembali = ""
        results = []
        for dahan in anak(tree):
            if data(dahan) == "package_thing":
                res = token(dahan)
                results.append(res)
        kembali += f"package {'.'.join(results)}"
        return kembali

    def package_item(self, tree):
        """
        item
          package_item
            keyword_package
            package_things
              package_thing     main
        """
        kembali = ""
        for dahan in anak(tree):
            if data(dahan) == "package_things":
                kembali += self.package_things(dahan)
        return kembali

    def do_generate(self):
        """
        self.root either item atau item_separator
        """
        # self.output += f'mengoprek data: {self.root.data}\n'
        # item
        self.indentno = 0
        if self.root.data == "item":
            for dahan in anak(self.root):
                # block_item
                if dahan.data == "block_item":
                    self.block_item(dahan)
                elif dahan.data == "statement_item":
                    self.statement_item(dahan)
                elif data(dahan) == "import_item":
                    self.import_item(dahan)
                elif data(dahan) == "package_item":
                    res = self.package_item(dahan)
                    self.output += res

        elif self.root.data == "item_separator":
            if self.root.children:  # jk bukan []
                newline_or_not = self.root.children[0].data
                self.output += f"\tSEP: {newline_or_not}\n"

    def generate(self):
        try:
            self.do_generate()
        except Exception as err:
            pesan = traceback.format_exc()
            print(pesan)
        return self.output


def generate(RootNode, program_context={}):
    # print('generate (py) called for ', RootNode)
    g = Generator(RootNode, program_context)
    return g.generate()
