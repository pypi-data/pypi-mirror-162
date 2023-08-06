from .peta_tipe_data import peta_tipe_data

self_indentno = 0
self_tabspace = "  "


def self_tab(tabno=0):
    return self_tabspace * (tabno if tabno else self_indentno)


def tabify_content(content):
    tabify = [self_tab() + item for item in content.splitlines()]
    return "\n".join(tabify)


def tabify_contentlist(content):
    tabify = [self_tab() + item for item in content]
    return "\n".join(tabify)


def dec():
    global self_indentno
    self_indentno -= 1 if self_indentno > 0 else 0


def inc():
    global self_indentno
    self_indentno += 1
