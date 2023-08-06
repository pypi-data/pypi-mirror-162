# import re
from langutils.app.stringutils import tabify_content, tabify_contentlist
from langutils.app.treeutils import (
    anak,
    data,
    token,
    child1,
    child2,
    child3,
    child4,
    child,
    chdata,
    chtoken,
    ispohon,
    istoken,
    beranak,
    sebanyak,
    jumlahanak,
)

indent = 0
# TAB = ' '*2
TAB = "\t"


def inc():
    global indent
    indent += 1


def dec():
    global indent
    indent -= 1


def tab():
    global indent
    return TAB * indent


def element_name(tree):
    kembali = token(tree)
    return kembali


def element_children(tree):
    """
    tree adlh tuple
    itemsnya adlh Tree
    """
    # print('elem child terima data:', type(tree), data(tree))
    anaks = []
    for tuple_item in anak(tree):  # tree
        # print(' >> elem child iterate:', type(tuple_item), tuple_item) # tuple
        for item in tuple_item:
            res = declarative_element(item)
            anaks.append(res)

    return "\n".join(anaks)


def item_key_value_berslash(tree):
    kembali = ""
    k, v = "", ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "item_key":
            k = token(item)
        elif jenis == "item_value_berslash":
            v = token(item)
            # print('value beraslash:', v, 'dari:', jenis)
    kembali += f"{k}={v}"
    return kembali


def item_key_value(tree):
    kembali = ""
    # kvs = []
    k, v = "", ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "item_key":
            k = token(item)
        elif jenis == "item_value":
            v = token(item)
        # kvs.append(f'{k} = {v}')
    kembali += f"{k}={v}"
    return kembali


def item_key_value_boolean(tree):
    """
    daripada:
    disabled=true
    mending:
    disabled
    """
    name = token(tree)
    # kembali = f'{name}=true'
    kembali = f"{name}"
    return kembali


def element_config(tree):
    kembali = ""
    kvs = []
    for item in anak(tree):
        jenis = data(item)
        if jenis == "item_key_value":
            kv = item_key_value(item)
            kvs.append(kv)
        elif jenis == "item_key_value_berslash":
            kv = item_key_value_berslash(item)
            kvs.append(kv)
        elif jenis == "item_key_value_boolean":
            kv = item_key_value_boolean(item)
            kvs.append(kv)
    kembali += " ".join(kvs)
    return kembali


def declarative_element(tree):
    kembali = ""
    name, attrs, children, text = "", "", "", ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "element_name":
            name = element_name(item)
        elif jenis == "element_config":
            attrs = element_config(item)
        elif jenis == "element_children":
            children = element_children(item)
        elif jenis == "cdata_text":
            text = token(item)
    kembali += f"<{name}"
    if attrs:
        kembali += " " + attrs
    kembali += ">\n"
    if text:
        inc()
        content = tabify_content(text, tab())
        kembali += content
        dec()
        kembali += "\n"
    if children:
        inc()
        content = tabify_content(children, tab())
        kembali += content
        dec()
        kembali += "\n"
    kembali += f"</{name}>"
    return kembali


def handler(tree):
    kembali = declarative_element(tree)
    return kembali
