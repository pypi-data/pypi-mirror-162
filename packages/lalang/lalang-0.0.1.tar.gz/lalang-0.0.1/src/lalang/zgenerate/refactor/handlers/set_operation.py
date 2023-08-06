from app.transpiler.zgenerate.refactor.handlers import expression_item
from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def set_operation(tree, identifier, language="py"):
    kembali = ""

    for item in anak(tree):
        if data(item) == "penanda":
            pass
        elif data(item) == "insert_at_tail":  # ?S+
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.add({hasil})"
        elif data(item) == "concat_extend_update":  # ?S+=
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
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
            hasil = expression_item.expression_item(ei, language=language)
            # kembali += f'{hasil} in {identifier}'
            kembali += f"{identifier}.includes({hasil})"
        elif data(item) == "count":
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.count({hasil})"
        elif data(item) == "clear":
            kembali += f"{identifier}.clear()"
        elif data(item) == "is_empty":
            kembali += identifier
        elif data(item) == "remove_item":
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.remove({hasil})"
        elif data(item) == "remove_item_silent":
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
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
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.union({hasil})"
        elif data(item) == "intersection":
            """
            https://www.w3schools.com/python/ref_set_intersection.asp
            set.intersection(set1, set2 ... etc)
            The intersection() method returns a set that contains the similarity between two or more sets.
            Meaning: The returned set contains only items that exist in both sets, or in all sets if the comparison is done with more than two sets.
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.intersection({hasil})"
        elif data(item) == "difference":
            """
            set.difference(set)
            https://www.w3schools.com/python/ref_set_difference.asp
            The difference() method returns a set that contains the difference between two sets.
            Meaning: The returned set contains items that exist only in the first set, and not in both sets.
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.difference({hasil})"
        elif data(item) == "symmetric_difference":
            """
            https://www.w3schools.com/python/ref_set_symmetric_difference.asp
            set.symmetric_difference(set)
            The symmetric_difference() method returns a set that contains all items from both set, but not the items that are present in both sets.
            Meaning: The returned set contains a mix of items that are not present in both sets.
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.symmetric_difference({hasil})"
        elif data(item) == "is_disjoint":
            """
            gak ada persamaan sama sekali...
            The isdisjoint() method returns True if none of the items are present in both sets, otherwise it returns False.
            https://www.w3schools.com/python/ref_set_isdisjoint.asp
            set.isdisjoint(set)
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.isdisjoint({hasil})"
        elif data(item) == "is_subset":
            """
            https://www.w3schools.com/python/ref_set_issubset.asp
            set.issubset(set)
            The issubset() method returns True if all items in the set exists in the specified set, otherwise it retuns False.
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.issubset({hasil})"
        elif data(item) == "is_superset":
            """
            https://www.w3schools.com/python/ref_set_issuperset.asp
            set.issuperset(set)
            The issuperset() method returns True if all items in the specified set exists in the original set, otherwise it retuns False.
            """
            ei = child1(item)
            hasil = expression_item.expression_item(ei, language=language)
            kembali += f"{identifier}.issuperset({hasil})"

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
