import functools
import json
import math
import os
import pprint
import re
import textwrap
from itertools import islice
from itertools import zip_longest as zeal

import click
from anytree.render import RenderTree
from pygments import highlight
from pygments.formatters import (NullFormatter, TerminalFormatter,
                                 TerminalTrueColorFormatter)
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexer import RegexLexer, words
# https://github.com/pygments/pygments/tree/master/pygments/lexers
# https://github.com/pygments/pygments/blob/master/pygments/lexers/_mapping.py
# https://pygments.org/docs/quickstart/
from pygments.lexers import (ClojureLexer, CppLexer, CSharpLexer, GoLexer,
                             HaskellLexer, HtmlLexer, JavascriptLexer,
                             NginxConfLexer, PythonLexer, ScalaLexer,
                             YamlLexer, get_lexer_by_name,
                             get_lexer_for_filename)
from pygments.lexers.python import PythonLexer
from pygments.token import Keyword, Name, Text

from .datetimeutils import format_epoch_longer
from .dirutils import latest_files, timeify_filelist
from .fileutils import file_content
from .utils import env_exist, env_get, env_int, trycopy, trypaste

lexer_map = {
    "clj": ClojureLexer,
    "cpp": CppLexer,
    "cs": CSharpLexer,
    "go": GoLexer,
    "hs": HaskellLexer,
    "html": HtmlLexer,
    "java": JavascriptLexer,
    "nginx": NginxConfLexer,
    "py": PythonLexer,
    "scala": ScalaLexer,
    "yaml": YamlLexer,
}


class MyLexer(PythonLexer):

    fuck_object = None

    def my_callback(lexer, match):
        kata = match.group(1)
        if kata in MyLexer.fuck_object.keywords:
            yield match.start(), Name.Builtin, kata
        else:
            yield match.start(), Text, kata

    tokens = {
        "root": [
            # (words(('file', 'capcay')), Name.Builtin),
            # (words(('file', 'capcay')), Name.Builtin),
            (r"\s+", Text),
            (r"(\w+)", my_callback),
            (r"\W+", Text),
        ],
    }

    def __init__(self, keywords):
        self.keywords = keywords

        MyLexer.fuck_object = self
        self.stripall = True
        self.tabsize = 2
        self.ensurenl = True
        self.filters = []
        # print('hasil tokens:', self.tokens)

    # def get_tokens_unprocessed(self, text):
    # 	for index, token, value in PythonLexer.get_tokens_unprocessed(self, text):
    # 		if token is Name and value in self.keys:
    # 			yield index, Keyword.Pseudo, value
    # 			# yield index, Name.Builtin, value
    # 		else:
    # 			yield index, token, value


def indah(
    message,
    warna="green",
    layar=None,
    width=80,
    newline=False,
    bold=True,
    blink=False,
    underline=True,
    reverse=True,
):
    """
    warna apa aja? https://pypi.org/project/colorama/
            black red green yellow blue magenta cyan reset"""
    try:
        # click.echo ( click.style(message.center(width), fg=warna, bg=layar, bold=True, blink=True, underline=True, reverse=True).decode('utf-8') )
        click.echo(
            click.style(
                message.center(width),
                fg=warna,
                bg=layar,
                bold=bold,
                blink=blink,
                underline=underline,
                reverse=reverse,
            ),
            nl=newline,
        )

    except Exception as e:
        print(str(e))
        print(message)


def indah0(
    message,
    warna="green",
    newline=False,
    layar=None,
    bold=False,
    blink=False,
    underline=False,
    reverse=False,
):
    """
    left justified
    default: 80 column, centered
    """
    indah(
        message,
        warna=warna,
        width=0,
        newline=newline,
        layar=layar,
        bold=bold,
        blink=blink,
        underline=underline,
        reverse=reverse,
    )


def indah1(
    message, warna="green", layar=None, blink=False, underline=False, reverse=False
):
    """
    newline
    bold
    """
    # indah0(message, warna, layar, bold=True, newline=True)
    indah(
        message,
        warna=warna,
        width=0,
        newline=True,
        layar=layar,
        bold=True,
        blink=blink,
        underline=underline,
        reverse=reverse,
    )


def indah2(
    message, warna="green", layar=None, blink=False, underline=False, reverse=False
):
    """
    newline
    bold
    copy
    """
    # indah0(message, warna, layar, bold=True, newline=True)
    indah(
        message,
        warna=warna,
        width=0,
        newline=True,
        layar=layar,
        bold=True,
        blink=blink,
        underline=underline,
        reverse=reverse,
    )
    trycopy(message)


def indah3(
    message,
    warna="green",
    layar=None,
    blink=False,
    underline=False,
    reverse=False,
    newline=True,
):
    """
    safe indah2 jk message kosong
    mengcopy pesan ke clipboard

    newline
    bold
    copy
    """
    if not message:
        return

    indah(
        message,
        warna=warna,
        width=0,
        newline=newline,
        layar=layar,
        bold=True,
        blink=blink,
        underline=underline,
        reverse=reverse,
    )
    trycopy(message)


def indah4(
    message,
    warna="green",
    layar="black",
    blink=False,
    underline=False,
    reverse=False,
    newline=True,
):
    """
    versi no copy clipboard dari indah3
    """
    if not message:
        return

    indah(
        message,
        warna=warna,
        width=0,
        newline=newline,
        layar=layar,
        bold=True,
        blink=blink,
        underline=underline,
        reverse=reverse,
    )


def indahnl(
    message,
    warna="green",
    layar=None,
    bold=False,
    newline=False,
    blink=False,
    reverse=False,
    underline=False,
):
    """
    newline
    """
    # indah0(message, warna, layar, bold=True, newline=True)
    indah(
        message,
        warna=warna,
        width=0,
        newline=True,
        layar=layar,
        bold=bold,
        blink=blink,
        underline=underline,
        reverse=reverse,
    )


def indahr(
    message,
    warna="green",
    layar=None,
    bold=False,
    newline=False,
    blink=False,
    underline=False,
):
    """
    newline
    reverse
    """
    # indah0(message, warna, layar, bold=True, newline=True)
    indah(
        message,
        warna=warna,
        width=0,
        newline=True,
        layar=layar,
        bold=bold,
        blink=blink,
        underline=underline,
        reverse=True,
    )


def indahb(
    message,
    warna="green",
    layar=None,
    newline=False,
    blink=False,
    underline=False,
    reverse=False,
):
    """
    newline
    bold
    """
    # indah0(message, warna, layar, bold=True, newline=True)
    indah(
        message,
        warna=warna,
        width=0,
        newline=True,
        layar=layar,
        bold=True,
        blink=blink,
        underline=underline,
        reverse=reverse,
    )


def indahu(
    message,
    warna="green",
    layar=None,
    newline=False,
    bold=False,
    blink=False,
    reverse=False,
):
    """
    newline
    underline
    """
    # indah0(message, warna, layar, bold=True, newline=True)
    indah(
        message,
        warna=warna,
        width=0,
        newline=True,
        layar=layar,
        bold=bold,
        blink=blink,
        underline=True,
        reverse=reverse,
    )


def print_list(the_list, genap="yellow", ganjil="green"):
    for index, filename in enumerate(the_list):
        tulisan = f"{index}. {filename}"
        warna = genap if (index % 2 == 0) else ganjil
        # indah0(tulisan, warna=warna, newline=True)
        indah4(tulisan, warna=warna)


def print_list_warna(
    the_list,
    genap="yellow",
    ganjil="green",
    bold=True,
    berwarna=True,
    special_ends=None,
    start=0,
    prefix="",
    extra_warna={},
    extra_suffix="",
    no_index=False,
):
    """
    contoh special_ends
    *.py
    maka highlight yg endswith tsb
    UPD:
    tambah extra_suffix utk bs kasih extra newline di antara baris
    tambah no_index jk gak mau ada index
    """
    for index, filename in enumerate(the_list, start):
        # print(f"proses {index} dan {filename}.")
        tulisan = (
            prefix
            + ("" if no_index else f"{index}. ")
            + f"{filename}"
            + (extra_suffix if extra_suffix else "")
        )
        if berwarna:
            warna = genap if (index % 2 == 0) else ganjil
            if extra_warna:
                for k, v in extra_warna.items():
                    if index % k == 0:
                        warna = v
            if special_ends and filename.endswith(special_ends):
                indah0(tulisan, warna="white", layar="red", bold=bold, newline=True)
            else:
                indah0(tulisan, warna=warna, bold=bold, newline=True)
        else:
            print(tulisan)


def print_json(data, indent=4, warna="yellow", layar="black"):
    indah4(json.dumps(data, indent=indent), warna=warna, layar=layar)


def pp(data):
    pprint.pprint(data)


def ppr(data):
    from rich.pretty import pprint

    pprint(data)


def print_tree(node):
    from anytree import RenderTree

    print(RenderTree(node))


def get_tree(node):
    from anytree import RenderTree

    return RenderTree(node)


def filter_print_latest_files(code, basedir, cetak_waktu=False):
    """
    kita nanti pengen bikin gini
    |50 word1 word2
    jadi dari hasil |50 kita filter yg mengandung word1 dan word2 saja.
    """
    # print(f'cetak latest files [code={code}], [dir={basedir}]')
    if not code:
        code = "10"  # minimal bertujuan utk lihat latest files

    m = re.match(r"^(\d+)\s*(.*)", code)
    if m:
        # print(f"ketemu m dg group: {m.groups()}")
        jumlah = m.group(1)
        jumlah = int(jumlah)
        result = latest_files(basedir, jumlah)

        # jk ada words utk ngefilter hasil ls by time
        allfilters = m.group(2)
        if allfilters:
            """
            di sini tentu pake any
            """
            splittedfilters = allfilters.split()
            # print(f"splitted: {splittedfilters}")
            result = [
                item
                for item in result
                if any([word for word in splittedfilters if word in item])
            ]
            # print(f"result: {result}")

        if cetak_waktu:
            # print(f"sblm timeify")
            result_with_time = timeify_filelist(
                result
            )  # latest_files_with_time(basedir, jumlah)
            # print(f"sblm print list warna")
            print_list_warna(result_with_time)
            return result_with_time
        else:
            print_list_warna(result)
            return result


def print_file(filepath):
    print(file_content(filepath))


def indah_file(filepath, warna="green", layar="black"):
    indah3(file_content(filepath), warna=warna, layar=layar)


def print_copy(content):
    print(content)
    trycopy(content)


def print_copy_file(filename, warna="white", pygments=False, lexer="py"):
    header = f"{'='*40} {filename}"
    content = file_content(filename)
    trycopy(content)
    # print(header)
    indah0(header, warna=warna, newline=True)

    if not pygments:
        print(content)
    else:
        default_lexer = lexer_map[lexer]()
        filename, extension = os.path.splitext(filename)
        if extension:
            choose = [item for item in lexer_map.keys() if extension == "." + item]
            if choose:
                choose = choose[0]
                default_lexer = lexer_map[choose]()

        print(highlight(content, default_lexer, TerminalTrueColorFormatter()))
        # print(highlight(content, get_lexer_for_filename(filename), NullFormatter()))
        # print(highlight(content, get_lexer_for_filename(filename), TerminalTrueColorFormatter()))


def dir_w_old(list_files, jumlah_kolom=None, screen_width=None):
    if env_exist("ULIBPY_DIR_W_SCREENWIDTH") or not screen_width:
        screen_width = int(env_get("ULIBPY_DIR_W_SCREENWIDTH"))

    if env_exist("ULIBPY_DIR_W_COLNUMBER") or not jumlah_kolom:
        jumlah_kolom = env_int("ULIBPY_DIR_W_COLNUMBER")

    pecah = lambda asli, banyak: [
        asli[i : i + banyak] for i in range(0, len(asli), banyak)
    ]

    terbagi = pecah(list_files, jumlah_kolom)

    kolomku = f"{{: >{screen_width / jumlah_kolom}}}"
    # [ print(f"{kolomku*3}".format(*item)) for item in b(list(range(0,9)),3) ]
    for item in terbagi:
        print(f"{kolomku*len(item)}".format(*item))


def dir_w(
    sumber_array,
    jumlah_kolom=None,
    screen_width=None,
    warna="blue",
    layar=None,
    bold=True,
):
    if env_exist("ULIBPY_DIR_W_SCREENWIDTH") or not screen_width:
        screen_width = int(env_get("ULIBPY_DIR_W_SCREENWIDTH"))

    if env_exist("ULIBPY_DIR_W_COLNUMBER") or not jumlah_kolom:
        jumlah_kolom = env_int("ULIBPY_DIR_W_COLNUMBER")

    def print_transposed(terbagi):
        kolomku = f"{{: <{int(screen_width/jumlah_kolom)}}}"
        for item in terbagi:
            # bersihkan elem dari item yg None
            item = [el for el in item if el is not None]
            indah0(
                f"{kolomku*len(item)}".format(*item),
                warna=warna,
                layar=layar,
                bold=bold,
                newline=True,
            )

    def transpose(array):
        return list(map(list, zeal(*array)))

    def ice(array, *args):
        return list(islice(array, *args))

    ambil = math.ceil(len(sumber_array) / jumlah_kolom)
    urut = [
        ice(sumber_array, ambil * oper, ambil * (oper + 1))
        for oper in range(jumlah_kolom)
    ]
    transposed = transpose(urut)
    print_transposed(transposed)


# filedir/library.py
def print_enumerate(contentlist):
    for index, item in enumerate(contentlist):
        print("{:4d}| {:s}".format(index, item))


def indah_enumerate(contentlist, warna="white"):
    for index, item in enumerate(contentlist):
        cetak = "{:4d}| {:s}".format(index, item)
        indah0(cetak, newline=True, bold=True, warna=warna)


def print_copy_enumerate_filtercontent(string_content, filterpattern, warna="green"):
    index_lines = enumerate(string_content.splitlines())
    content = [
        "{:4d}| {:s}".format(no, baris)
        for (no, baris) in index_lines
        if filterpattern in baris
    ]
    trycopy(content)
    for line in content:
        indah3(line, warna=warna)


def print_copy_enumerate(content):
    trycopy(content)
    for index, item in enumerate(content.splitlines()):
        print("{:4d}| {:s}".format(index, item))


def print_copy_enumerate_list(contentlist, delimiter=""):
    """
    spt print_copy_enumerate
    tapi input adlh list, jd gak perlu splitlines() dulu
    """
    trycopy(delimiter.join(contentlist))
    for index, item in enumerate(contentlist):
        print("{:4d}| {:s}".format(index, item))


def print_debug(*args, **kwargs):
    if env_int("ULIBPY_FMUS_DEBUG"):
        print(*args, **kwargs)


def indah_debug(*args, **kwargs):
    if env_int("ULIBPY_FMUS_DEBUG"):
        indah4(*args, **kwargs)


class Debug:
    def __init__(self, isDebug=False, printToFile=""):
        # self.isDebug = isDebug
        self.isDebug = env_int("ULIBPY_FMUS_DEBUG")
        # input(f'nilai debug adlh [{self.isDebug}] dan args [{isDebug}] ')
        if printToFile:
            self.filename = printToFile
            self.fd = open(self.filename, "a")

    def stop(self):
        if hasattr(self, "filename"):
            if self.fd:
                os.close(self.fd)

    def __call__(self, *args, **kwargs):
        """
        kita kasih kwargs: forced
        if forced == True maka print bagaimanapun
        """
        # print('debug is called', 'debug?', self.isDebug, 'kwargs', kwargs)
        if self.isDebug:
            if hasattr(self, "filename"):
                print(*args, **kwargs, file=self.fd)
            else:
                # indah0(*args, **kwargs)
                if len(args) == 1 and isinstance(args[0], str):
                    pesan = args[0]
                    indah0(pesan, **kwargs, reverse=True)
                else:
                    print(*args, **kwargs)
        else:
            if kwargs and "forced" in kwargs and kwargs["forced"]:
                del kwargs["forced"]
                input("forcing debug!")
                if len(args) == 1 and isinstance(args[0], str):
                    pesan = args[0]
                    indah0(pesan, **kwargs)
                else:
                    print(*args, **kwargs)


def pigmen(content, keywords):
    print(highlight(content, MyLexer(keywords), TerminalFormatter()))
    # lexer = MyLexer()
    # state_item = (words(tuple(keywords)), Name.Builtin)
    # lexer.tokens = {
    # 	'root': [
    # 		state_item,
    # 		(r'\s+', Text),
    # 		(r'\w+', Text),
    # 		(r'\W+', Text),
    # 	],
    # }
    # print(highlight(content, lexer, TerminalFormatter()))


def print_file_pigmen(filepath, keywords):
    pigmen(file_content(filepath), keywords)


def printex(msg="", printer=print):
    import traceback

    printer(msg)
    printer(traceback.format_exception())


def tryex(block_content, msg="", printer=print):
    import traceback

    try:
        block_content()
    except Exception as err:
        printer(f"{msg}: {err}")
        printer(traceback.format_exception())
