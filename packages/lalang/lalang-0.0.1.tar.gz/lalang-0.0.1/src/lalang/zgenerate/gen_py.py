import json
import traceback

from app.dirutils import here, joiner, new_filename_timestamp, tempdir
from app.printutils import print_enumerate
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, istoken, jumlahanak,
                           sebanyak, token)
from app.utils import env_int, tidur

from .common import MyJsonify

# from typing import ...
peta_tipe_data = {
    "char": "string",
    "integer": "number",
    "float": "number",
    "string": "string",
    "boolean": "boolean",
    "any": "any",
    "void": "void",
}


class Generator:
    def __init__(self, RootNode, program_context):
        self.root = RootNode
        self.program_context = program_context
        self.indentno = 0
        self.output = ""
        # self.tabspace = '\t'
        self.tabspace = " " * 2

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
        tabify = [self.tab() + item for item in content.splitlines()]
        return "\n".join(tabify)

    def tabify_contentlist(self, content):
        tabify = [self.tab() + item for item in content]
        return "\n".join(tabify)

    def dec(self):
        self.indentno -= 1 if self.indentno > 0 else 0

    def inc(self):
        self.indentno += 1

    def literal_bool(self, nilailiteral):
        # nilai = True if nilailiteral.data == 'boolean_true' else False
        nilai = "True" if nilailiteral.data == "boolean_true" else "False"
        return nilai

    def literal_number(self, nilailiteral):
        """
        konversi ke int jadi sering bikin
        can only concatenate str (not "int") to str
        """
        # nilailiteralstr = int(nilailiteral.children[0])
        nilailiteralstr = str(nilailiteral.children[0])
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
            da_string = da_string.replace("/", "{", 1).replace("/", "}", 1)
        nilailiteralstr = 'f"' + da_string + '"'
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

    def literal(self, tree):
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
        """
        kembali = ""
        for item in anak(tree):
            jenis = data(item)
            if jenis == "literal_string":
                kembali += self.literal_string(item)
            elif jenis == "literal_char":
                kembali += self.literal_char(item)
            elif jenis == "literal_number":
                kembali += self.literal_number(item)
            elif jenis == "literal_list":
                hasil_list = self.literal_list(item)
                kembali += str(hasil_list).replace("'", "")
            elif jenis == "literal_dict":
                kembali += self.literal_dict(item)
            elif jenis == "template_string":
                kembali += self.template_string(item)
            elif jenis.startswith("boolean"):
                kembali += self.literal_bool(item)

        return kembali

    def enum_member(self, tree):
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
        for item in anak(memberlist):
            if data(item) == "enum_member":
                hasil = self.enum_member(item)
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

        from .common import python_enum_info

        hasil = python_enum_info
        hasil = ["// " + item for item in hasil.splitlines()]
        hasil = "\n".join(hasil) + "\n"
        hasil += "import enum\n"
        hasil += f"class {nama_enum}(enum.Enum):\n{isi_enum}"
        return hasil

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
        return f"({right}){left}"

    def member_index_expression(self, tree):
        """
        member_index_expression
          expression_item
            nama_identifier s
          expression_item
            nama_identifier A
        """
        container, key = "", ""
        for item in anak(tree):
            if data(item) == "expression_item":
                if not container:
                    container = self.expression_item(item, returning=True)
                else:
                    key = self.expression_item(item, returning=True)
        return f"{container}[{key}]"

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
        elif data(literal) == "member_index_expression":
            hasil = self.member_index_expression(literal)
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
        # return f' = {nilai_variable}'
        return nilai_variable

    def tipe_identifier(self, tree):
        kembali = ""
        for item in anak(tree):
            if data(item) == "tipe_data_buatan":
                kembali = chtoken(item)
            else:
                jenis = data(item)
                kembali = peta_tipe_data.get(jenis, jenis)
        return kembali

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
        kembali = ""
        for dahan in anak(tree):
            if data(dahan) == "declaration_config":
                pass
            elif data(dahan) == "declaration_name":
                declaration_name = token(dahan)
                if returning:
                    kembali += declaration_name
                else:
                    self.print(declaration_name)
            elif data(dahan) == "tipe_identifier":
                # jenis = data(child1(dahan))
                # tipe_native = peta_tipe_data.get(jenis, jenis)
                pass
                # tipe_native = self.tipe_identifier(dahan)
                # if returning:
                #   kembali += f': {tipe_native}'
                # else:
                #   self.print(f': {tipe_native}')
            elif data(dahan) == "declaration_value":
                # ei = child1(dahan)
                # nilai_variable = self.expression_item(ei, returning=True)
                nilai_variable = self.declaration_value(dahan)
                if returning:
                    kembali += f" = {nilai_variable}"
                else:
                    self.print(f" = {nilai_variable}")
        return kembali

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
        kembali = ""
        for dahan in anak(tree):
            if data(dahan) == "declaration_config":
                pass
            elif data(dahan) == "declaration_name":
                declaration_name = token(dahan)
                if returning:
                    kembali += declaration_name
                else:
                    self.print(declaration_name)
            elif data(dahan) == "tipe_identifier":
                pass
                # jenis = data(child1(dahan))
                # tipe_native = peta_tipe_data.get(jenis, jenis)
                # if returning:
                #   kembali += f': {tipe_native}'
                # else:
                #   self.print(f': {tipe_native}')
            elif data(dahan) == "declaration_value":
                ei = child1(dahan)
                if data(ei) == "expression_item":
                    nilai_variable = self.expression_item(ei, returning=True)
                    if returning:
                        kembali += f" = {nilai_variable}"
                    else:
                        self.print(f" = {nilai_variable}")
                elif data(ei) == "instantiation_expression":
                    """
                    $c=*MyClass()
                    """
                    # print('instantiation_expression #1')
                    hasil = self.instantiation_expression(ei, returning=True)
                    # print('instantiation_expression #2')
                    hasil = " = " + hasil  # nama = hasil
                    if returning:
                        kembali += hasil
                    else:
                        self.print(hasil)

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
                return f"print({nilai})"

    def set_operation(self, tree, identifier):
        """
        https://www.w3schools.com/python/python_ref_set.asp
        item_at
        concat_extend_update
        insert_at_tail
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "penanda":
                pass
            elif data(item) == "insert_at_tail":  # ?S+
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.add({hasil})"
            elif data(item) == "concat_extend_update":  # ?S+=
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.update({hasil})"
            elif data(item) == "item_pop":  # ?S/
                kembali += f"{identifier}.pop()"
            elif data(item) == "item_pop_but_stay":  # ?S//
                # https://stackoverflow.com/questions/59825/how-to-retrieve-an-element-from-a-set-without-removing-it
                kembali += f"next(iter({identifier}))"
            elif data(item) == "length":
                kembali += f"len({identifier})"
            elif data(item) == "contains":
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{hasil} in {identifier}"
            elif data(item) == "count":
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.count({hasil})"
            elif data(item) == "clear":
                kembali += f"{identifier}.clear()"
            elif data(item) == "is_empty":
                kembali += identifier
            elif data(item) == "remove_item":
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.remove({hasil})"
            elif data(item) == "remove_item_silent":
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.discard({hasil})"
            elif data(item) == "to_string":
                kembali += f"str({identifier})"

            elif data(item) == "union":
                """
                https://www.w3schools.com/python/ref_set_union.asp
                set.union(set1, set2...)
                The union() method returns a set that contains all items from the original set, and all items from the specified set(s).
                You can specify as many sets you want, separated by commas.
                It does not have to be a set, it can be any iterable object.
                If an item is present in more than one set, the result will contain only one appearance of this item.
                """
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.union({hasil})"
            elif data(item) == "intersection":
                """
                https://www.w3schools.com/python/ref_set_intersection.asp
                set.intersection(set1, set2 ... etc)
                The intersection() method returns a set that contains the similarity between two or more sets.
                Meaning: The returned set contains only items that exist in both sets, or in all sets if the comparison is done with more than two sets.
                """
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.intersection({hasil})"
            elif data(item) == "difference":
                """
                set.difference(set)
                https://www.w3schools.com/python/ref_set_difference.asp
                The difference() method returns a set that contains the difference between two sets.
                Meaning: The returned set contains items that exist only in the first set, and not in both sets.
                """
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.difference({hasil})"
            elif data(item) == "symmetric_difference":
                """
                https://www.w3schools.com/python/ref_set_symmetric_difference.asp
                set.symmetric_difference(set)
                The symmetric_difference() method returns a set that contains all items from both set, but not the items that are present in both sets.
                Meaning: The returned set contains a mix of items that are not present in both sets.
                """
                ei = child1(item)
                hasil = self.symmetric_difference(ei)
                kembali += f"{identifier}.discard({hasil})"
            elif data(item) == "is_disjoint":
                """
                gak ada persamaan sama sekali...
                The isdisjoint() method returns True if none of the items are present in both sets, otherwise it returns False.
                https://www.w3schools.com/python/ref_set_isdisjoint.asp
                set.isdisjoint(set)
                """
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.isdisjoint({hasil})"
            elif data(item) == "is_subset":
                """
                https://www.w3schools.com/python/ref_set_issubset.asp
                set.issubset(set)
                The issubset() method returns True if all items in the set exists in the specified set, otherwise it retuns False.
                """
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.issubset({hasil})"
            elif data(item) == "is_superset":
                """
                https://www.w3schools.com/python/ref_set_issuperset.asp
                set.issuperset(set)
                The issuperset() method returns True if all items in the specified set exists in the original set, otherwise it retuns False.
                """
                ei = child1(item)
                hasil = self.expression_item(ei)
                kembali += f"{identifier}.issuperset({hasil})"
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
        """format
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
        data_operation
          array_operation
            penanda
            map
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
            elif data(item) == "remove_by_value":
                """
                lst?A-'arrow'
                """
                ei = child1(item)
                thing = self.expression_item(ei)
                # index = identifier.indexOf(item)
                # if (index != -1) { identifier.splice(index, 1) }
                kembali += f"{identifier}.remove({thing})"
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
                kembali += (
                    f"for index, {iden} in enumerate({identifier}):\n{self.tab()}pass"
                )
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

    def initialize_with_faker(self, tree):
        """
        myarr?An$5:s
        myarr?An$5:i
        """

        kembali = ""
        jumlah_data, isi_data = "", ""
        for item in anak(tree):
            # print('oprek item bertipe:', type(item), item)
            if istoken(item):
                jumlah_data = str(item)  # jangan token(item) yg ambil children
            elif data(item) == "tipe_identifier":
                isi_data = self.tipe_identifier(item)

        from app.fakerutils import getfakers

        funcnames = {
            "string": "word",
            "int": "pyint",
            "number": "pyint",
        }
        hasil = getfakers(funcnames[isi_data], int(jumlah_data))
        # from app.fakerutils import get_by_datatypes
        # hasil = get_by_datatypes(isi_data, int(jumlah_data))

        kembali += hasil
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
                kembali = f"json.dumps({hasil}, indent=2)"
            elif data(item) == "json_in":
                ei = child1(item)
                hasil = self.expression_item(ei, returning=True)
                kembali = f"json.loads({hasil})"
        # print('kembali file/json operation:', kembali)
        return kembali

    def gui_operation(self, tree):
        """
        gui_operation: penanda "u" gui_operation_config? gui_operation_cmd
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "penanda":
                pass
            elif data(item) == "gui_operation_config":
                pass
            elif data(item) == "gui_operation_cmd":
                pass
        return kembali

    def react_operation(self, tree, identifier):
        """
        react_operation: penanda "@" react_operation_config? react_operation_cmd
        /py/data?@usestate
        """
        from .helper.react_helper import process_cmd

        kembali = ""
        for item in anak(tree):
            if data(item) == "penanda":
                pass
            elif data(item) == "react_operation_config":
                pass
            elif data(item) == "react_operation_cmd":
                command = token(item).strip()
                hasil = process_cmd(command, identifier)
                kembali = hasil
        # print('react #3', kembali)
        return kembali

    def datetime_operation(self, tree, identifier):
        """
        penanda "d" datetime_operation_config? datetime_operation_choice
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "datetime_operation_config":
                pass
            elif data(item) == "now_datetime":
                """
                ?dn
                ?dndd-mm-yyyy hh:nn:ss
                ?dnyyyy-mm-dd hh:nn:ss
                """
                if beranak(item):
                    setter = child1(item)
                    date_fields = []
                    time_fields = []
                    if data(setter) == "set_datetime":
                        for setx in anak(setter):
                            if data(setx) == "set_date":
                                for cucu in anak(setx):
                                    # print('set_date', cucu, 'bertipe:', type(cucu))
                                    if istoken(cucu):
                                        cucu = str(cucu)
                                        date_fields.append(cucu)
                            elif data(setx) == "set_time":
                                for cucu in anak(setx):
                                    # print('set_time', cucu, 'bertipe:', type(cucu))
                                    if istoken(cucu):
                                        cucu = str(cucu)
                                        time_fields.append(cucu)
                    datetime_string, date_string, time_string = "", "", ""
                    if date_fields:
                        year_first = True
                        if len(date_fields[0]) == 4:
                            year_first = True
                        if len(date_fields[2]) == 4:
                            year_first = False
                        if year_first:
                            date_string = (
                                f"{date_fields[0]}-{date_fields[1]}-{date_fields[2]}"
                            )
                        else:
                            date_string = (
                                f"{date_fields[2]}-{date_fields[1]}-{date_fields[0]}"
                            )
                        datetime_string = date_string
                    if time_fields:
                        time_string = (
                            f"{time_fields[0]}:{time_fields[1]}:{time_fields[2]}"
                        )
                        datetime_string += " " + time_string
                    kembali += f'const {identifier} = new Date("{datetime_string}")'
                else:
                    kembali += f"const {identifier} = new Date()"
            elif data(item) == "now_date":
                pass
            elif data(item) == "now_time":
                pass
            elif data(item) == "day_of_week":
                kembali += f"{identifier}.getDay()"  # 0 = sunday
            elif data(item) == "day_of_year":
                pass
            elif data(item) == "week_of_year":
                pass
            elif data(item) == "yyyy_year":
                kembali += f"{identifier}.getFullYear()"
            elif data(item) == "yy_year":
                pass
            elif data(item) == "mm_month":
                pass
            elif data(item) == "m_month":
                kembali += f"{identifier}.getMonth()"
            elif data(item) == "dd_day":
                pass
            elif data(item) == "d_day":
                kembali += f"{identifier}.getDate()"
            elif data(item) == "hh_hour_24":
                pass
            elif data(item) == "hh_hour_12":
                pass
            elif data(item) == "h_hour_24":
                kembali += f"{identifier}.getHours()"
            elif data(item) == "h_hour_12":
                pass
            elif data(item) == "tt_minute":
                kembali += (
                    f"{identifier}.getMinutes().padStart({identifier}.getMinutes(), 0)"
                )
            elif data(item) == "t_minute":
                kembali += f"{identifier}.getMinutes()"
            elif data(item) == "ss_second":
                kembali += (
                    f"{identifier}.getSeconds().padStart({identifier}.getSeconds(), 0)"
                )
            elif data(item) == "s_second":
                kembali += f"{identifier}.getSeconds()"
            elif data(item) == "epoch_second":
                kembali += f"{identifier}.getTime() / 1000"
            elif data(item) == "epoch_millisecond":
                kembali += f"{identifier}.getTime()"
            elif data(item) == "epoch_microsecond":
                kembali += f"{identifier}.getTime() * 1000"
            elif data(item) == "to_iso":
                # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString
                kembali += f"{identifier}.toISOString()"
            elif data(item) == "to_string":
                kembali += f"{identifier}.toString()"
            elif data(item) == "from_string":
                """
                | "4s" set_date -> from_string // parse, ?d4s2021-08-24
                """
                date_fields = []
                year_first = False
                for putih in anak(item):
                    if data(putih) == "set_date":
                        for merah in anak(putih):
                            if istoken(merah):
                                merah = str(merah)
                                date_fields.append(merah)
                        year_first = len(date_fields[0]) == 4
                if year_first:
                    year, month, date = date_fields
                else:
                    date, month, year = date_fields
                from app.datetimeutils import month3

                month = month3[int(month) - 1]  # 3 = March
                datetime_string = f"{month} {date}, {year}"
                kembali += f'const {identifier} = Date.parse("{datetime_string}")'
            elif data(item) == "add_year":
                nilai = token(item)
                kembali += f"{identifier}.setYear({identifier}.getYear() + {nilai});"
            elif data(item) == "add_month":
                nilai = token(item)
                kembali += f"{identifier}.setMonth({identifier}.getMonth() + {nilai});"
            elif data(item) == "add_day":
                # d.setDate(d.getDate() + 50);
                nilai = token(item)
                kembali += f"{identifier}.setDate({identifier}.getDate() + {nilai});"
            elif data(item) == "add_hour":
                nilai = token(item)
                kembali += f"{identifier}.setHours({identifier}.getHours() + {nilai});"
            elif data(item) == "add_minute":
                nilai = token(item)
                kembali += (
                    f"{identifier}.setMinutes({identifier}.getMinutes() + {nilai});"
                )
            elif data(item) == "add_second":
                kembali += (
                    f"{identifier}.setSeconds({identifier}.getSeconds() + {nilai});"
                )
            elif data(item) == "add_millisecond":
                kembali += f"{identifier}.setMilliseconds({identifier}.getMilliseconds() + {nilai});"
            elif data(item) == "set_year":
                """
                tgl?d=y/1978/08/24 => tgl.setFullYear(1978, 08, 24);
                """
                nilai = token(item)
                if jumlahanak(item) == 3:
                    nilai += f", {token(item, 1)}, {token(item, 2)}"
                kembali += f"{identifier}.setFullYear({nilai})"
            elif data(item) == "set_month":
                nilai = token(item)
                kembali += f"{identifier}.setMonth({nilai})"
            elif data(item) == "set_day":
                # d.setDate(d.getDate() + 50);
                nilai = token(item)
                kembali += f"{identifier}.setDate({nilai})"
            elif data(item) == "set_hour":
                nilai = token(item)
                kembali += f"{identifier}.setHours({nilai})"
            elif data(item) == "set_minute":
                nilai = token(item)
                kembali += f"{identifier}.setMinutes({nilai})"
            elif data(item) == "set_second":
                nilai = token(item)
                kembali += f"{identifier}.setSeconds({nilai})"
            elif data(item) == "set_millisecond":
                nilai = token(item)
                kembali += f"{identifier}.setMilliseconds({nilai})"
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
        /py/iden?AM#(){?+'hello';?+'aca aca aca jimmy'}
        """
        kembali = ""
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
            if funcargs:
                ok = getattr(faker, funcname)(*funcargs)
                # print('\t\tok:', ok)
            else:
                ok = getattr(faker, funcname)()

            if isinstance(ok, int):
                ok = str(ok)
            elif isinstance(ok, list):
                ok = str(ok)
            elif isinstance(ok, dict):
                ok = json.dumps(ok, indent=2, cls=MyJsonify)
            elif isinstance(ok, str):
                ok = '"' + ok + '"'
            # print('faker ops call:', ok, 'bertipe:', type(ok))
            hasil.append(ok)

        # /py/?K5/pydict(5,False)
        # print('faker ops hasil:', hasil, 'bertipe:', type(hasil))

        if as_string:
            return ", ".join(hasil)
        return "[" + ", ".join(hasil) + "]"

    def fmus_run(self, program, capture_outerr=True):
        from app.fmus import Fmus

        fmus = Fmus(env_int("ULIBPY_FMUS_DEBUG"))
        # fmus.set_file_dir_template(filepath)
        # fmus.set_file_template(filepath)
        # fmus.set_dir_template_from_file(filepath)
        fmus.process(program, capture_outerr=capture_outerr)
        if capture_outerr and "$*" in program:
            tidur(ms=env_int("ULIBPY_STDOUT_CAPTURE_SLEEP_MS"))
            if fmus.stdout or fmus.stderr:
                self.print(fmus.stdout if fmus.stdout else fmus.stderr)

    def run_fmus_with_editor(self, filepath, initial_text="", title="New FMUS program"):
        from editor import editor

        program = editor(filepath, initial_text=initial_text, title=title)
        if program.strip():
            program = program + "\n"
            print("************")
            print(program)
            print("************")
            self.fmus_run(program)

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
        ini bukan versi mk file krn gak ada baris-entry
        harus dukung !!N utk versi mk file...
        """
        from editor import editor

        code = ""
        filepath = joiner(tempdir(), new_filename_timestamp())  # + '.mk'

        for item in anak(tree):
            if data(item) == "fmus_execute":
                code = token(item)
                if code.strip():
                    program = code + "\n"
                    self.fmus_run(program)
            elif data(item) == "fmus_run_file":
                # !!R#pola filename
                # from app.fileutils import file_content
                # from app.dirutils import here
                # fmus_source = joiner(here(__file__), 'helper/fmus/code-terminal.mk')
                # fmus_code_terminal = file_content(fmus_source)
                # self.run_fmus_with_editor(filepath, initial_text=fmus_code_terminal)
                # fmus_run_file: "R#" HURUF_DIGIT_SPASI
                cari_file = token(item)
                from .helper.fmus_helper import fmus_run_file

                fmus_run_file(cari_file, filepath)
            elif data(item) == "fmus_new":
                for basefile in anak(item):
                    if data(basefile) == "fmus_new_basedir":
                        basedir = token(basefile)
                        filepath = joiner(basedir, new_filename_timestamp())
                    elif data(basefile) == "fmus_new_filename":
                        filename = token(basefile)
                        filepath = joiner(tempdir(), filename)
                    elif data(basefile) == "fmus_new_filepath":
                        filepath = token(basefile)
                # pastikan filepath ada dan basedir terbuat
                program = editor(filepath)
                if program.strip():
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

    def redis_operation_config(self, tree):
        """
        redis_operation_config
          redis_operation_config_items
            redis_dbname_config 7
        """
        kembali = {}
        redis_operation_config_items = child1(tree)
        for item in anak(redis_operation_config_items):
            if data(item) == "redis_dbname_config":
                kembali["db"] = token(item)
            elif data(item) == "redis_host_config":
                kembali["host"] = token(item)
            elif data(item) == "redis_port_config":
                kembali["port"] = token(item)
            # elif data(item) == 'redis_username_config':
            #   kembali['username'] = token(item)
            elif data(item) == "redis_password_config":
                kembali["password"] = token(item)
            # elif data(item) == 'redis_schema_config':
            #   kembali['schema'] = token(item)
        return kembali

    def redis_operation(self, tree):
        """ """
        from app.transpiler.zgenerate.helper.redis_helper import redis_process

        kembali = ""
        cmd, thing, hasil = "", "", ""
        redisconf = {}
        args = []
        for item in anak(tree):
            if data(item) == "penanda":
                pass
            elif data(item) == "redis_operation_config":
                hasil = self.redis_operation_config(item)
                redisconf.update(hasil)
                args.append(redisconf)
            elif data(item) == "redis_string_get":
                cmd = "get"
            elif data(item) == "redis_string_add":
                cmd = "set"
            elif data(item) == "redis_keys":
                cmd = "list"
            elif data(item) == "redis_exists":
                cmd = "exists"
            elif data(item) == "redis_connect":
                cmd = "connect"  # ?r/d=7/c
            elif data(item) == "redis_reset":
                cmd = "reset"  # ?rr
            elif data(item) == "redis_key":
                thing = token(item)
                args.append(thing)
            elif data(item) == "redis_value":
                thing = token(item)
                args.append(thing)
            elif data(item) == "redis_args":
                args = self.redis_args(item)

        if cmd:
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
        """
        instantiation_expression
          new_operator
          nama_identifier     MyClass
          function_call_param
        """
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
                jenis = chdata(item)  # python gak pake type sementara
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
                nama, _, nilai = self.named_value(nv)
                args.append(f"{nama}={nilai}")
        return ", ".join(args)

    def function_call_param(self, funcparam, add_self=False, returning=True):
        """
        function_param utk deklarasi/definisi fungsi
        function_call_param utk pemanggilan fungsi/method/constructor

        function_call_param
          callparamlist
            callparam
              literal
                literal_string        hello
        instantiation_expression
          new_operator
          nama_identifier     MyClass
          function_call_param

        """
        if not beranak(funcparam):
            return "()"

        # function_call_param hanya punya 1 anak
        # callparamlist
        funcparamlist = child1(funcparam)
        if anak(funcparamlist):
            actualargs = []
            # print('iterate funcparamlist.children:', funcparamlist.children)
            for param in funcparamlist.children:
                # callparam
                # print('func call param:', param)
                # nama_identifier or named_values
                if not param.children:
                    continue
                namaid = param.children[0]
                if namaid.data == "nama_identifier":
                    # print('param nama_identifier')
                    argid = str(namaid.children[0])
                    actualargs.append(argid)
                elif namaid.data == "named_values":
                    # print('param named_values')
                    for kv in namaid.children:
                        # named_value = kv
                        # namaidentifier = str(kv.children[0].children[0])
                        # nilaiidentifier = kv.children[1]
                        # ei = nilaiidentifier.children[0]
                        # lit = ei.children[0]
                        # nilaiidentifierstr = self.literal(lit)
                        namaidentifier, _, nilaiidentifierstr = self.named_value(kv)
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
        keyname, range_start_value = "", ""
        for item in anak(tree):
            if data(item) == "nama_jenis_identifier_optional":
                keyname = self.nama_jenis_identifier_optional(item)
            elif data(item) == "expression_item":
                range_start_value = self.expression_item(item)

        # print(f'for_start: {keyname}, {range_start_value}')
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
            return f"{keyname} in range({range_start}, {range_end}):\n"
        else:
            return f"{keyname} in range({range_start}, {range_end}, {forstep}):\n"

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

    def for_each(self, tree):
        """
        "@" for_each "@"  // for@item/items/index@
        for_each: item_name "/" array_name ("/" key_name)?
        for_each
          item_name   item
          array_name  items
        """
        # item = token(child1(tree))
        # items = token(child2(tree))
        # if anak(tree)==3:
        #   index = token(child3(tree))
        #   return f"{index}, {item} in enumerate({items})"

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

        return f"{index}, {value} in enumerate({items})"

    def for_in(self, tree):
        """
        "#" for_in "#"    // for#key/items#
        for_in: key_name "/" array_name
        for_in
          key_name
            nama_jenis_identifier_optional
              nama_identifier i
          array_name
            nama_identifier   items
        """
        index, items = "", ""
        for item in anak(tree):
            if data(item) == "key_name":
                """
                for_in
                  key_name
                    nama_jenis_identifier_optional
                      nama_identifier i
                """
                nama_jenis_identifier_optional = child1(item)
                index = self.nama_jenis_identifier_optional(
                    nama_jenis_identifier_optional
                )
            elif data(item) == "array_name":
                items = chtoken(item)

        return f"{index}, _ in enumerate({items})"

    def for_of(self, tree):
        """ """
        value, items = "", ""
        for item in anak(tree):
            if data(item) == "item_name":
                """ """
                nama_jenis_identifier_optional = child1(item)
                value = self.nama_jenis_identifier_optional(
                    nama_jenis_identifier_optional
                )
            elif data(item) == "array_name":
                for cucu in anak(item):
                    if data(cucu) == "nama_identifier":
                        things = chtoken(item)
                    elif data(cucu) == "expression_item":
                        things = self.expression_item(cucu)
        return f"{value} in {items}"

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
            if returning:
                return f"{self.tab()}pass"
            else:
                self.print(f"{self.tab()}pass")

    def for_statement(self, tree, returning=True):
        """
        for_statement
          for_keyword
          condition_for
          condition_body

        for(){}
        for@@{}
        for##{}
        for$${}
        """
        kembali, forname, forcondition, forbody = "", "", "", ""
        for item in anak(tree):
            if data(item) == "for_keyword":
                forname = "for"
            elif data(item) == "condition_for":
                forcondition = self.condition_for(item)
                # print('peroleh for condition', forcondition)
            elif data(item) == "condition_body":
                self.inc()
                forbody = self.condition_body(item, returning=True)
                # print('peroleh for body', forbody)
                self.dec()
        # forbody termasuk ':', no space dg condition
        kembali = f"{forname} {forcondition}{forbody}"
        if returning:
            return kembali
        self.print(kembali)

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
                # if not output.endswith(';'):
                #   output += ';'
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
        """
        kembali = ""  # digunakan oleh returning
        if beranak(funccontent):
            # functioncontentlist
            functioncontentlist = child1(funccontent)
            hasil = self.functioncontentlist(functioncontentlist)
            if hasil:
                return hasil
            else:
                # f(){} empty funcbody
                if returning:
                    return kembali + f"\n{self.tab()}pass"
                else:
                    self.output += f"\n{self.tab()}pass"
        else:
            if returning:
                return kembali + f"\n{self.tab()}pass"
            else:
                self.output += f"\n{self.tab()}pass"

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
        for statement in anak(tree):
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

        anonymous_function
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
        # harus ada mode: arrow func atau normal func
        # default adlh arrow func
        # print('oprek anon func utk', tree.pretty())
        # arrow_func_mode = True
        # arrow_uses_expression = True
        # kembali = ''
        is_arrow_func_or_lambda = True  # jk hanya 1 expr
        funcparams, funcbody = "", ""
        internal, external = "", ""
        for item in anak(tree):
            if data(item) == "non_arrow_func":
                is_arrow_func_or_lambda = False
            elif data(item) == "function_param":
                funcparams = self.function_param(item, returning=True)
            elif data(item) == "anon_expression":
                hasil = self.anon_expression(item)
                internal = f"lambda item: {hasil}"
            elif data(item) == "anon_statements":
                badan_fungsi = self.anon_statements(item)
                if len(badan_fungsi) == 1 and is_arrow_func_or_lambda:
                    hasil = badan_fungsi[0]
                    if funcparams == "()":
                        funcparams = "item"
                    internal = f"lambda {funcparams}: {hasil}"
                else:
                    assign_name = "anon_func"
                    internal = assign_name
                    self.inc()  # hrs sblm proses tabify
                    funcbody = self.tabify_contentlist(badan_fungsi)
                    self.dec()
                    if funcparams == "()":
                        funcparams = "(item)"
                    # self.inc()
                    external = f"def {assign_name}{funcparams}:\n" + funcbody + "\n"
                    # self.dec()

        # external adlh: def myanon_func(): ...
        # internal adlh: map/filter/reduce(myanon_func, mylist)
        kembalian = {
            "internal": internal,
            "external": external,
        }
        return kembalian

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
                    # mestinya cek ini jk: not hasil['external']
                    asumsikan_oneliner = hasil["internal"]
                    args.append(asumsikan_oneliner)

        # kembalikan list
        return args

    def function_call(self, tree):
        """
        function_call
          function_name print
          argument_list
            argument
              expression_item
                literal
                  literal_number        1
            argument
              expression_item
                literal
                  literal_number        2
        function_call
          function_name     print
          argument_list
            argument
              expression_item
                literal
                  literal_string        hello
        function_call
          function_name             print
        function_call
          function_name
            nama_identifier_with_typeparams
              nama_identifier       MyClass
        """
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
        """
        f:foo(){}
        selalu ada function_param ()
        dan function_content {}

        function_item
          keyword_function
          function_name     foo
          function_param
          function_content

        function_item
          function_name     foo
          function_param
            paramlist
              *
              param
                nama_identifier     satu
              param
                nama_identifier     dua
          function_content
            functioncontentlist
              functioncontent
        """
        self.inc()
        kembali = ""
        for item in anak(cucu):
            if data(item) == "keyword_function":
                pass
            elif data(item) == "function_name":
                name = self.function_name(item)
                kembali += "def " + name
            elif data(item) == "function_param":
                param = self.function_param(item, returning=True)
                kembali += param + ":"
            elif data(item) == "function_content":
                content = self.function_content(item, returning=True)
                kembali += "\n" + content

        if returning:
            return kembali

        self.print(kembali)
        self.dec()

    def constructor_content(self, ctor_method_field):
        """ """
        kembali = f"\n{self.tab()}def __init__"
        # self.output +=
        self.inc()
        # function_param
        ctorparam = child1(ctor_method_field)
        kembali += self.function_param(ctorparam, add_self=True, returning=True)
        kembali += ":"
        # function_content
        ctorcontent = child2(ctor_method_field)
        kembali += self.function_content(ctorcontent, returning=True)
        self.dec()
        return kembali

    def method_content(self, tree, structname=None):
        """
        method_content
          function_name
            nama_identifier_with_typeparams
              nama_identifier       len
          function_param
          function_content
        """
        kembali = ""
        for item in anak(tree):
            # print('method content item:', item)
            if data(item) == "function_name":
                nama_identifier_with_typeparams = child1(item)
                nama = self.nama_identifier_with_typeparams(
                    nama_identifier_with_typeparams
                )
                #
                # instance = f'# {structname.lower()}1 = {structname}.new'
                # calling = f'# {structname.lower()}1.{nama}'
                # kembali += instance + '\n'
                # kembali += calling + '\n'
                kembali += f"def {nama}"
                print("peroleh func name:", kembali)
            elif data(item) == "tipe_identifier":
                # tipe_identifier = self.tipe_identifier(item)
                pass
            elif data(item) == "function_param":
                print("mau func param:")
                kembali += self.function_param(item, add_self=True, returning=True)
                kembali += ":"
                print("peroleh func param:", kembali)
            elif data(item) == "function_content":
                kembali += "\n"  # stlh param...
                self.inc()
                kembali += self.function_content(item, returning=True)
                self.dec()
                print("peroleh func content:", kembali)

        return kembali

    def fieldconfiglist(self, tree):
        """
        fieldconfig: "+" -> public
          | "-" -> private
          | "#" -> protected
          | "ro" -> read_only       // readonly name: string = "world"; hanya assign dlm ctor
          | "%" -> static
        """
        semua_modifier = []
        is_static = False
        for nilai in anak(tree):
            if data(nilai) == "public":
                hasil = "public"
                semua_modifier.append(hasil)
            elif data(nilai) == "private":
                hasil = "private"
                semua_modifier.append(hasil)
            elif data(nilai) == "protected":
                hasil = "protected"
                semua_modifier.append(hasil)
            elif data(nilai) == "read_only":
                hasil = "readonly"
                semua_modifier.append(hasil)
            elif data(nilai) == "static":
                is_static = True

        if semua_modifier:
            return " ".join(semua_modifier) + " ", is_static
        return "", is_static

    def field_content(self, tree):
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
        kembali = ""
        # default_field_config = 'self.'
        field_config, field_name, field_type, field_value = "", "", "", ""
        is_static = False
        for item in anak(tree):
            if data(item) == "field_config":
                # masih bermasalah: jk specify #, + dll, self.<nama> jadi hilang utk non-static
                configlist = child1(item)
                field_config, is_static = self.fieldconfiglist(configlist)
            elif data(item) == "field_name":
                field_name = token(item)
                # masukkan self.<username> di sini
                # kembali += default_field_config
                # kembali += nama
            elif data(item) == "tipe_identifier":
                field_type = self.tipe_identifier(item)
                # kembali += f': {tipe_native}'
                pass
            elif data(item) == "declaration_value":
                field_value = self.declaration_value(item)
                # kembali += f' = {nilai}'

        # print(f'hasil field content = [{kembali}]')
        return field_config, field_name, field_type, field_value, is_static

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
        # constructor_content
        if not beranak(tree):
            return None, None
        ctor_method_field = child1(tree)
        if ctor_method_field.data == "constructor_content":
            item = self.constructor_content(ctor_method_field)
            # collected_content.append(item)
            return item, "ctor"
        elif data(ctor_method_field) == "method_content":
            item = self.method_content(ctor_method_field, structname=structname)
            return item, "method"
        elif data(ctor_method_field) == "field_content":
            (
                field_config,
                field_name,
                field_type,
                field_value,
                is_static,
            ) = self.field_content(ctor_method_field)
            # return item
            return [
                field_config,
                field_name,
                field_type,
                field_value,
                is_static,
            ], "field"

    def classcontentlist(self, tree, structname=None):
        """
        class_content -> classcontentlist -> classcontent
        classcontentlist
          classcontent
          classcontent
        """

        def create_initialize_method(members):
            """
            name: [config,name,type,value,is-static]
            """
            # print('create_initialize_method #1')
            # cust1 = Customer.new("1", "John", "Wisdom Apartments, Ludhiya")
            index_value = 3
            value_list = ", ".join([item[index_value] for item in members.values()])
            instance = f"# {structname.lower()}1 = {structname}({value_list})"
            # print('create_initialize_method #2', instance)
            hasil = instance + "\n"
            # print('hasil #1', hasil)
            hasil += f'def __init__(self, {", ".join(members.keys())})\n'
            # print('hasil #2', hasil)
            self.inc()
            for k, v in members.items():
                hasil += self.tab() + f"self.{k} = {k}\n"
            # print('hasil #3', hasil)
            self.dec()
            return hasil

        collected_content = []
        initialize_method_member = {}
        initmethod = ""

        for classcontent in anak(tree):
            hasil, jenis = self.classcontent(classcontent, structname=structname)
            if jenis is not None and jenis == "field":
                # initialize_method_member.update(hasil)
                # hasil = 0=config,1=name, 2=type, 3=value, 4=is static
                if hasil[4]:  # is_static
                    name_value = f"{hasil[1]} = {hasil[3]}"
                    collected_content.append(name_value)
                else:
                    initialize_method_member.update({hasil[1]: hasil})
            elif hasil:
                collected_content.append(hasil)

        if initialize_method_member:
            # print('sblm bikin def init:', initialize_method_member)
            initmethod = create_initialize_method(initialize_method_member)
            # print('peroleh initmethod', initmethod)

        if collected_content:
            tabbed_class_contents = [self.tab() + item for item in collected_content]
            tabbed_class_contents = "\n".join(tabbed_class_contents)
            if initmethod:
                initializer = [self.tab() + item for item in initmethod.splitlines()]
                initializer = "\n".join(initializer)
                pemisah = f'\n{"#"*20}\n'
                kembali = (
                    "\n" + initializer + pemisah + "\n" + tabbed_class_contents + "\n"
                )
            else:
                kembali = "\n" + tabbed_class_contents + "\n"
        elif initmethod:
            initializer = [self.tab() + item for item in initmethod.splitlines()]
            initializer = "\n".join(initializer)
            pemisah = f'\n{"#"*20}\n'
            kembali = "\n" + initializer
        else:
            # no content jadi {} utk ts dan pass utk python
            # self.print('{}')
            kembali = f"\n{self.tab()}pass"

        return kembali

    def class_content(self, class_content, structname=None):
        """
        class_content
          classcontentlist
            classcontent
        """
        # classcontentlist
        classcontentlist = child1(class_content)
        if beranak(classcontentlist):
            """
            classcontent
              constructor_content
                function_param
                  paramlist
                    param
                function_content
                  functioncontentlist
                    functioncontent
            """
            hasil = self.classcontentlist(classcontentlist, structname=structname)
            self.print(hasil)

        else:
            self.print(f"\n{self.tab()}pass")

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
        return namaid

    def paramlist(self, tree):
        """
        function_param
          paramlist <- tree
            param
              nama_identifier     satu
        """
        all_params = []
        # print('paramlist tree', tree)
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

        # print('all_params:', all_params)
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

    def nama_identifier_or_literal(self, tree):
        """
        nama_identifier_or_literal
          nama_identifier       cherry
        """
        kembali = ""
        for item in anak(tree):
            if data(item) == "nama_identifier":
                kembali = token(item)
            elif data(item) == "literal":
                kembali = self.literal(item)
        return kembali

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
            # print('beranak 1 #1')
            class_namestr = chtoken(tree)
            # print(f'beranak 1 #1: {class_namestr}')

        return class_namestr

    def class_item(self, cucu):
        """
        class_item
          class_name        MyClass
          class_content
            classcontentlist
              classcontent
        """
        self.inc()
        # class_name
        class_name = child1(cucu)
        class_namestr = ""
        if chdata(class_name) == "nama_identifier_with_typeparams":
            nama_identifier_with_typeparams = child1(class_name)
            class_namestr = chtoken(nama_identifier_with_typeparams)
        elif chdata(class_name) == "nama_identifier":
            class_namestr = token(class_name)
        self.output += f"class {class_namestr}:"
        # class_content
        class_content = child2(cucu)
        self.class_content(class_content, structname=class_namestr)
        self.dec()

    def block_item(self, tree):
        kembali = ""
        for cucu in anak(tree):
            if cucu.data == "function_item":
                kembali += self.function_item(cucu)
            elif cucu.data == "class_item":
                kembali += self.class_item(cucu)
            elif cucu.data == "interface_item":
                kembali += self.interface_item(cucu)
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

    def searchable(self, tree, filepath="data/import_py.txt"):
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
                filepath = joiner(here(__file__), "../data/import_py.txt")
                print("filepath:", filepath)
                hasil = self.searchable(item, filepath)

        if search_mode:
            pass  # hasil sudah berisi yg diminta
        else:
            if container:
                hasil = f'from {container} import {", ".join(merged_imports)}'
            else:
                hasil = f'import {", ".join(merged_imports)}'

        self.output += hasil

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
