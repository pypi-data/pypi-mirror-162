from langutils.app.dirutils import ayah, here, joiner, joinhere
from langutils.app.fileutils import file_blocks
from langutils.app.greputils import pattern_search_list, pattern_search_string

filename = "snippets.txt"
filepath = joinhere(__file__, "data", filename)
delimiter = "###"


content_cache = None


def content():
    global content_cache
    if not content_cache:
        content_cache = file_blocks(filepath, delimiter=delimiter)
    return content_cache


def cari(isi):
    # return [item for item in content() if isi in item]
    return pattern_search_list(content(), isi)


def cari_asstring(isi):
    found = pattern_search_list(content(), isi, aslist=True)
    print(f"terima found: [{found}]")
    if found:
        if len(found) == 1:
            return found[0]
        else:
            return ("$$$").join(found)
    return ""
