from anytree import AnyNode, AsciiStyle, Node, PreOrderIter, RenderTree
from anytree.importer import DictImporter, JsonImporter
from anytree.search import find, findall

from .stringutils import tabify_contentlist
from .usutils import tab_tab


def get_root(node):
    if not hasattr(node, "parent") or not node.parent:
        return node
    return get_root(node.parent)


def get_parent(node, match_condition=lambda x: x.counter == 0, pass_condition=None):
    """
    condition misalnya lambda x: hasattr(x, 'type') and x.type=='RootNode'
    bisa juga tentunya: lambda x: x.counter == -1 dan x.name == 'info' utk peroleh %__TEMPLATE_key=value

    cara kerja:
    jk sebuah node penuhi match_condition maka return node
    jk node gak punya parent maka return node

    spt nya pass_condition belum perlu:
    jk sebuah node penuhi pass_condition maka kita lewati node itu dan pass kan parentnya utk diproses
    """
    if match_condition(node):
        return node

    # ini jadi mengembalikan semua node dong, krn semua gak punya parent???
    # or anynode dah otomatis assign parent? spt nya sih begitu, lihat kondisi utk rekursifnya di sini
    if not hasattr(node, "parent") or not node.parent:
        return node
    return get_parent(node.parent, match_condition, pass_condition)


def get_all_parent_variables(node, result={}):
    """
    pemilik vars seringnya tidak satu track dg yg butuh...jadi gak ketemu
    """
    while node.counter != 0:
        # print('[get_all_parent_variables] process node:', node.counter)
        if hasattr(node, "variables"):
            result.update(node.variables)
        return get_all_parent_variables(node.parent, result)

    # skrg sudah pada root, proses dulu semua direct children dari root
    # yes, ini berhasil
    for anak_kandung in get_direct_children(node):
        if hasattr(anak_kandung, "variables"):
            result.update(anak_kandung.variables)
    return result


def item_workdir_has_input(item):
    """
    /input/
    /input		<- kita cek ini dulu
    """
    from .utils import env_get

    return "/" + env_get("ULIBPY_FMUS_INPUT_KEYWORD") in item.workdir


def replace_if_input_and_parent_is_dir(item):
    """
    AnyNode(counter=7,
    level=3,
    name='proshop4',
    old_name='__TEMPLATE_APPNAME',
    operations=['create_dir'],
    original='__TEMPLATE_APPNAME,d(/mk)',
    type='dir',
    workdir='/mnt/c/work/oprek/fshelp/fslang/utils/proshop4')

    item.workdir = /mnt/c/work/oprek/fshelp/fslang/utils/input/__init__.py
    """
    from .dirutils import ayah
    from .printutils import indah4
    from .utils import env_get

    has_dir_parent = False
    kembali = item.workdir
    if hasattr(item, "parent") and item.parent:
        if item.parent.type == "dir" and ayah(item.parent.workdir, 1) == ayah(
            item.workdir, 2
        ):
            # extra checking
            if item.parent.name != env_get("ULIBPY_FMUS_INPUT_KEYWORD"):
                has_dir_parent = True
    # indah4(f"""
    # has_dir_parent								= {has_dir_parent}
    # item.parent.type							= {item.parent.type}
    # item.parent.name							= {item.parent.name}
    # ayah(item.parent.workdir,1)		= {ayah(item.parent.workdir,1)}
    # ayah(item.workdir,2)					= {ayah(item.workdir,2)}
    # """, warna='yellow', layar='green')
    if (
        ayah(item.workdir, 1).endswith(env_get("ULIBPY_FMUS_INPUT_KEYWORD"))
        and has_dir_parent
    ):
        kembali = kembali.replace(
            env_get("ULIBPY_FMUS_INPUT_KEYWORD"), item.parent.name
        )
        # indah4(f"[replace_if_input_and_parent_is_dir] ganti nama dari {env_get('ULIBPY_FMUS_INPUT_KEYWORD')} ke {item.parent.name}", warna='white', layar='blue')
    return kembali


def replace_workdir__INPUT__with_value_from_parent(item):
    """
    item:
            workdir='C:\\work\\tmp\\__INPUT__\\package.json'
    parent:
            workdir='C:\\work\\tmp\\emih'
                     ^^^^^^^^^^^^^  ^^^^^^^^^^
                     sama           beda
    """
    from .dirutils import ayah, basename
    from .utils import env_get

    parent = item.parent
    input_keyword = env_get("ULIBPY_FMUS_INPUT_KEYWORD")
    skip_input_item = ayah(item.workdir, 2)  # C:\\work\\tmp
    skip_input_parent = ayah(parent.workdir, 1)  # C:\\work\\tmp
    pengganti_dari_parent = basename(parent.workdir)  # emih
    current_item_parent = ayah(item.workdir, 1)  # C:\\work\\tmp\\__INPUT__
    yang_mau_diganti_dari_item = basename(current_item_parent)  # __INPUT__

    workdir_baru = item.workdir  # jika replace berikut gagal

    if (skip_input_item == skip_input_parent) and (
        yang_mau_diganti_dari_item == input_keyword
    ):
        workdir_baru = item.workdir.replace(input_keyword, pengganti_dari_parent)

    return workdir_baru


def get_all_tree_children(akar):
    children = []

    def get_children(root):
        if len(root.children) > 0:
            for anak in root.children:
                children.append(anak)
                get_children(anak)

    get_children(akar)
    return children


def get_last_absolute_children(akar):
    children = get_all_tree_children(akar)
    if len(children) > 0:
        return children[-1]
    return None


def get_direct_children(akar):
    return [node for node in akar.children]


def get_last_direct_children(akar):
    children = [node for node in akar.children]
    if len(children) > 0:
        return children[-1]
    return None


def set_attr_direct_children(akar, attribute, value):
    for node in akar.children:
        setattr(node, attribute, value)


def set_attr_direct_children_cond(akar, attribute, value_yes, value_no, condition):
    for node in akar.children:
        setattr(node, attribute, value_yes if condition else value_no)


def print_ready_children(item):
    children = get_all_tree_children(item)
    print_ready = [node.level * "  " + node.original for node in children]
    print_ready = "\n".join(print_ready)
    return print_ready


def get_siblings_all(akar, include_me=True):
    if include_me:
        return [node for node in akar.parent.children]
    else:
        return [node for node in akar.parent.children if node != akar]


def get_siblings_before(akar):
    """
    a masukkan
    b masukkan
    c masukkan
    d <- aku
    e
    """
    # aku = -1
    # for index, node in enumerate(akar.parent.children):
    # 	if node == akar:
    # 		aku = index
    # 		break
    # ambil index aku
    aku = [index for index, item in enumerate(akar.parent.children) if item == akar][0]
    return akar.parent.children[:aku]


def get_siblings_after(akar):
    aku = [index for index, item in enumerate(akar.parent.children) if item == akar][0]
    return akar.parent.children[aku + 1 :]


def get_previous_sibling(node):
    if not hasattr(node, "parent"):
        return None
    aku = [index for index, item in enumerate(node.parent.children) if item == node][0]
    if aku == 0:
        return None
    return node.parent.children[aku - 1]


def get_tables(root):
    node_tables = (
        lambda node: hasattr(node, "name")
        and node.name == "table"
        and node.type == "table"
    )
    tables = findall(root, node_tables)
    return tables


## berhub dg lark


def data(tree):
    return tree.data


def anak(tree):
    return tree.children


# ini gak jalan, lark Tree gak punya parent
import lark


def tipedata(tree):
    return type(tree)


def ispohon(tree):
    return isinstance(tree, lark.tree.Tree)


def istoken(tree):
    return isinstance(tree, lark.lexer.Token)


def isnode(tree):
    return isinstance(tree, AnyNode)


def bapak(tree):
    return tree.parent


def sebanyak(tree, n=0):
    return len(tree.children) == n


def jumlahanak(tree):
    return len(tree.children)


def beranak(tree, n=0):
    "bahaya: ini hanya utk minta boolean, bukan integer sbg kembalian"
    return len(tree.children) > n


def child(tree, n=0):
    if beranak(tree):
        if not n:  # minta anak pertama
            return child1(tree)
        # now n > 0
        if jumlahanak(tree) >= n:
            return tree.children[n - 1]
        # minta anak ke-2 tapi cuma ada 1 anak
        return None
    return None


def child1(tree):
    """
    tree = mytree
    | _ anak1 = anak2 = anak3 -> mytree
    maka di sini mytree punya child1, child2, dan child3
    """
    return tree.children[0]


def child2(tree):
    return tree.children[1]


def child3(tree):
    return tree.children[2]


def child4(tree):
    return tree.children[3]


def child5(tree):
    return tree.children[4]


def chdata(tree, n=0):
    """
    kembalikan child data ke-n-1
    chdata(tree, 2) minta child data utk child no 2 (children[1])
    pastikan jumlah anak dari tree >= 2
    """
    if beranak(tree):
        if not n:  # jk chdata(sometree) maka minta child pertama spt chdata0
            return chdata1(tree)
        if jumlahanak(tree) >= n:
            """
            chdata(tree, 4): minta data utk child ke 4
            """
            return data(tree.children[n - 1])
        # jk minta data ke-2 dan cuma ada 1 anak
        return None
    return None


def chdata1(tree):
    if beranak(tree):
        return data(child1(tree))
    return None


def chdata0(tree):
    """
    last data
    """
    if beranak(tree):
        total = beranak(tree)
        return data(tree.children[total - 1])
    return None


def token(tree, token_index=0, jenis="str"):
    """
    tree		value
    """
    if jenis == "int":
        return int(tree.children[token_index])
    if jenis == "float":
        return float(tree.children[token_index])
    if jenis == "bool":
        return bool(tree.children[token_index])
    return str(tree.children[token_index])


def chtoken(tree, n=0):
    """
    hanya utk direct child!
    tree
            child1			token
            child2			token
            child3			token
    bukan utk:
    tree
            child1
                    child1		<- ini bukan child2 !!
    """
    if beranak(tree):
        if not n:
            # berarti minta ch token anak pertama
            # chtoken(tree, n=0) ini setara dg chtoken(tree, n=1)
            return token(child1(tree))
        # skrg n > 0
        if jumlahanak(tree) >= n:
            # jk minta n = 2 maka jumlah anak hrs >= 2
            return token(child(tree, n))
        return None

    return None


def tables_from_rootnode(RootNode):
    """ """
    node_tables = (
        lambda node: hasattr(node, "model")
        and node.name == "table"
        and node.type == "table"
    )
    tables = findall(RootNode, node_tables)
    return tables


def get_first_column(TableNode, get_label=True):
    """
    app.transpiler.frontend.fslang.django.__init__
    """
    if get_label:
        return TableNode.children[0].label
    return TableNode.children[0]


column_assignment_doc = """
ini adlh utk sebuah table/tablename/document

paramlist
first, second, third

paramlist_value
first=first, second=second, third=third

pydict
"first": first, "second": second, "third": third

pydict_first
only first: "first": first

pydict_rest
tanpa first: "second": second, "third": third

paramlist_type (minta tabify dan delimiter)
PARAMLIST_COMMA
	delimiter ", "
	first: string, second: string, third: int
PARAMLIST_NEWLINE0
	delimiter \n
	first: string
	second: string
	third: int
PARAMLIST_NEWLINE1
	tabify 1 + delimiter \n
		first: string
		second: string
		third: int
"""

ASSIGNMENT_FIRSTCOLUMN = "__TEMPLATE_ASSIGNMENT_FIRSTCOLUMN"
ASSIGNMENT_PARAMLIST_SIMPLE = "__TEMPLATE_ASSIGNMENT_PARAMLIST_SIMPLE"
ASSIGNMENT_PARAMLIST_VALUE = "__TEMPLATE_ASSIGNMENT_PARAMLIST_VALUE"
ASSIGNMENT_PYDICT_ALL = "__TEMPLATE_ASSIGNMENT_PYDICT_ALL"
ASSIGNMENT_PYDICT_FIRST = "__TEMPLATE_ASSIGNMENT_PYDICT_FIRST"
ASSIGNMENT_PYDICT_REST = "__TEMPLATE_ASSIGNMENT_PYDICT_REST"
ASSIGNMENT_PARAMLIST_COMMA = "__TEMPLATE_ASSIGNMENT_PARAMLIST_COMMA"
ASSIGNMENT_PARAMLIST_NEWLINE0 = "__TEMPLATE_ASSIGNMENT_PARAMLIST_NEWLINE0"
ASSIGNMENT_PARAMLIST_NEWLINE1 = "__TEMPLATE_ASSIGNMENT_PARAMLIST_NEWLINE1"
ASSIGNMENT_PARAMLIST_PREFIX = "__TEMPLATE_ASSIGNMENT_PARAMLIST"


def assignment_paramlist_type(
    TableNode, pemetaan=None, delimiter=", ", num_tab=0, tabber=tab_tab
):
    from app.libpohon.handlers import type_mapper_by_provider

    result = []
    for col in TableNode.children:
        if pemetaan:
            jenis = type_mapper_by_provider[pemetaan][col.type]
        else:
            jenis = col.type
        entry = f"{col.label}: {jenis}"
        result.append(entry)
    result = tabify_contentlist(result, self_tab=tabber(num_tab), delim=delimiter)
    return result


def assignment_firstcolumn(TableNode):
    return TableNode.children[0].label


def assignment_paramlist(TableNode):
    """ """
    paramlist = []
    for i, col in enumerate(TableNode.children):
        paramlist.append(col.label)

    return ", ".join(paramlist)


def assignment_paramlist_value(TableNode):
    """ """
    paramlist = []
    for i, col in enumerate(TableNode.children):
        nilai = f"{col.label}={col.label}"
        paramlist.append(nilai)

    return ", ".join(paramlist)


def assignment_pydict_all(TableNode):
    """ """
    paramlist = []
    for i, col in enumerate(TableNode.children):
        nilai = f'"{col.label}": {col.label}'
        paramlist.append(nilai)

    return ", ".join(paramlist)


def assignment_pydict_first(TableNode):
    """ """
    col_label = TableNode.children[0].label
    return f'"{col_label}": {col_label}'


def assignment_pydict_rest(TableNode):
    """ """
    # jk hanya 1 maka gak usah...
    # if len(TableNode.children)==1:
    # 	col_label = TableNode.children[0].label
    # 	return f'"{col_label}": {col_label}'
    paramlist = [
        f'"{col.label}": {col.label}'
        for i, col in enumerate(TableNode.children)
        if i > 0
    ]
    return ", ".join(paramlist)
