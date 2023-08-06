import json
import re
import string

default_tab = " " * 2  # '\t'
SQ = "'"
DQ = '"'
BT = "`"
_SQ = SQ
_DQ = DQ
_BT = BT
__SQ = SQ
__DQ = DQ
__BT = BT
__SQ__ = SQ
__DQ__ = DQ
__BT__ = BT
QuoteChar = "$$$"
EmptyReplaceQuoteChar = ""


def jsonify(data, indent=4):
    return json.dumps(data, indent=indent)


def max_item_len_in_list(the_list):
    return max([len(item) for item in the_list])


def email_valid(email):
    """
    https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    """
    pat = "^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$"
    return re.search(pat, email)


def startswith_absolute_folder(text, pattern_suffix=""):
    """
    groups()
    group()
      AttributeError: 'NoneType' object has no attribute 'group'
    group(0)
    """
    if pattern_suffix:
        """
        jk diberikan ",d"
        maka kita True = yes startswith abspath hanya jk text diakhiri dg ",d" maka proses text sbg path
        """
        if not text.endswith(pattern_suffix):
            return False
    pat = "^(\/[^\/]+)+"
    return re.match(pat, text)


def strip0(text, prefix):
    return text.removeprefix(prefix).strip()


def strip1(text, suffix):
    return text.removesuffix(suffix).strip()


def remove_nondigits(text, replacer=""):
    pat = "[^0-9]"
    return re.sub(pat, replacer, text)


def hitung(text, char="|"):
    """
    hitung jumlah char dlm text
    """
    return text.count(char)


def ada(text, char):
    return hitung(text, char) > 0


def first_occurrence(text, char, start=0, end=-1):
    """
    https://stackoverflow.com/questions/2294493/how-to-get-the-position-of-a-character-in-python/2294502
    """
    return text.index(char, start, end)


def splitspace(text, count=1, delim=" "):
    """
    count=1
    'satu dua tiga empat' => ['satu', 'dua tiga empat']
    """
    return text.split(delim, count)


def list_startswith(the_list, the_start, lower=True):
    if lower:
        return [item for item in the_list if item.lower().startswith(the_start.lower())]
    else:
        return [item for item in the_list if item.startswith(the_start)]


def list_contains(the_list, the_start, lower=True):
    if lower:
        return [item for item in the_list if the_start.lower() in item.lower()]
    else:
        return [item for item in the_list if the_start in item]


def list_stringify(the_list, delimiter="\n", sort=True, prefixer=None, suffixer=None):
    if prefixer:
        the_list = [prefixer + item for item in the_list]
    if suffixer:
        the_list = [item + suffixer for item in the_list]
    if sort:
        return delimiter.join(sorted(the_list))
    return delimiter.join(the_list)


def gabung_kunci(the_dict, delimiter="\n", sort=True):
    if sort:
        return "\n".join(sorted(the_dict.keys()))
    return "\n".join(the_dict.keys())


def dari_kanan(sumber, karakter):
    return sumber.rfind(karakter)


def punctuation_in_string(text, with_space=False):
    allow_underscore = string.punctuation.replace("_", "")
    if with_space:
        allow_underscore += " "
    return [kar in allow_underscore for kar in text]


def get_first_punctuation_index(text, with_space=False):
    nonwords = r"[^\w]+"
    if with_space:
        nonwords = r"[^\w\s]+"
    all = re.findall(nonwords, text)
    # print('all puncs', all)
    if all:
        return text.index(all[0])
    return None


def is_camel_case(s):
    return s != s.lower() and s != s.upper() and "_" not in s


def pluralize(s):
    return s.lower() + "s"


def merge_lines(s, joiner="", strip=True):
    """
    joiner bisa juga space
    """
    linified = s.splitlines()
    if strip:
        linified = [item.strip() for item in linified]
    return joiner.join(linified)


def escape_quotes(s):
    return s.replace('"', '\\"')


def non_empty_lines(lines):
    return [item for item in lines if item.strip()]


def tabify_content(content, self_tab=default_tab, num_tab=1, delim="\n"):
    tabify = [num_tab * self_tab + item for item in content.splitlines()]
    return delim.join(tabify)


def tabify_content_tab(content, num_tab=1, delim="\n"):
    from .usutils import tab_tab

    return tabify_content(content, self_tab=tab_tab(), num_tab=num_tab, delim=delim)


def tabify_content_space(content, num_tab=1, delim="\n", space_size=2):
    from .usutils import tab_space

    return tabify_content(
        content, self_tab=tab_space(space_size=space_size), num_tab=num_tab, delim=delim
    )


def tabify_contentlist(
    content, self_tab=default_tab, num_tab=1, aslist=False, delim="\n", string_ender=""
):
    """
    string_ender
      jk pengen:
      a=1,
      b=2,
    """
    tabify = [num_tab * self_tab + item for item in content]
    if aslist:
        return tabify
    return delim.join(tabify) + string_ender


def tabify_contentlist_tab(
    content, num_tab=1, aslist=False, delim="\n", string_ender=""
):
    from .usutils import tab_tab

    return tabify_contentlist(
        content,
        self_tab=tab_tab(),
        num_tab=num_tab,
        aslist=aslist,
        delim=delim,
        string_ender=string_ender,
    )


def tabify_contentlist_space(
    content, num_tab=1, aslist=False, delim="\n", string_ender="", space_size=2
):
    from .usutils import tab_space

    return tabify_contentlist(
        content,
        self_tab=tab_space(space_size=space_size),
        num_tab=num_tab,
        aslist=aslist,
        delim=delim,
        string_ender=string_ender,
    )


def left_right_joinify_content(content, left="", middle="\n", right=""):
    """
    default: newline-joined
    """
    delimiter = left + middle + right
    return delimiter.join(content.splitlines())


def left_right_joinify_contentlist(content, left="", middle="\n", right=""):
    """
    default: newline-joined
    """
    delimiter = left + middle + right
    return delimiter.join(content)


def joinify_content(content, delimiter="\n"):
    """
    default: input dan output sama
    """
    return delimiter.join(content.splitlines())


def joinfy_contentlist(content, delimiter="\n"):
    return delimiter.join(content)


def clean_list_to_string(alist):
    """
    lst = [1,2,3,4,5] sbg list
    str(lst) = ['1','2','3','4','5'] sbg string
    clean_list_to_string = [1,2,3,4,5] sbg string
    """
    return str(alist).replace("'", "")


def dashToCamel(text):
    """
    dashToCamel('satu-dua-tiga-empat-lima')
    """
    hasil = text
    while "-" in hasil:
        b = hasil.index("-")
        hasil = hasil[:b] + hasil[b + 1].upper() + hasil[b + 2 :]
    return hasil


d2C = dashToCamel


def dash_to_camel(text):
    return dashToCamel(text)


def sort_list(da_list, panjang_duluan=False):
    return sorted(da_list, key=len, reverse=panjang_duluan)


def list_take_shortest(da_list):
    if len(da_list) == 1:
        return da_list[0]
    a = sort_list(da_list)
    # print('LTS list:', da_list)
    if len(a):
        return a[0]
    return None


def list_take_longest(da_list):
    # print('LTL list:', da_list)
    if len(da_list) == 1:
        return da_list[0]
    a = sort_list(da_list, panjang_duluan=True)
    if len(a):
        return a[0]
    return None


def newlinify(baris):
    if not baris.endswith("\n"):
        baris += "\n"
    return baris


def replace_non_alpha(text, pengganti="_", exclude="."):
    """
    exclude adlh \W yg gak direplace dg _
    kita pengen . gak direplace oleh _
    """
    # return re.sub('\W+', pengganti, text)
    return re.sub(r"[^\w" + exclude + "]", pengganti, text)


def splitstrip0(thelist):
    """
    split berbasis space dan selalu ALL fields
    """
    return [item.strip() for item in thelist.split()]


def splitstrip(thelist, delimiter=" ", maxsplit=-1):
    """
    bisa specify delimiter dan jumlah fields yg displit
    """
    return [item.strip() for item in thelist.split(delimiter, maxsplit)]


def joinsplitstrip(thelist, delimiter=" ", maxsplit=-1):
    return splitstrip(thelist, delimiter, maxsplit)


def joinsplitlines(thelist, pemisah="\n"):
    return pemisah.join(thelist.splitlines())


def joinsplitstriplines(thelist, pemisah="\n"):
    return pemisah.join([item.strip() for item in thelist.splitlines()])


def multiple_spaces_to_single_space(original_text, replacer=" "):
    """
    https://pythonexamples.org/python-replace-multiple-spaces-with-single-space-in-text-file/
    """
    # return ' '.join(original_text.split())
    return re.sub("\s+", replacer, original_text)


"""
dipake utk repace/insert utk fileoperation...@ia, @ra, @rs, dst.
misal:
"target": "es5" menjadi "target": "es6"
"module": "commonjs"
@rs="__DQtarget__DQ: __DQes6__DQ"="__DQtarget__DQ: __DQes5__DQ"

	def sanitize_prohibited_chars(self, content):
		kita bisa tulis DQ sbg pengganti double quote
		@re,baris_cari_dalam_mk_file,"something DQemphasizedDQ and other"
		lihat di h feature
		pubspec.yaml,f(f=pubspec.yaml,@ra=flutter_sdk_no="sdk: DQ>=2.")
		sebetulnya lebih baik jk kita gunakan
		__DQ daripada DQ doang...
		for k,v in chars_to_sanitize_in_file_operation.items():
			content = content.replace(k, v)

		return content

TODO:
pake juga utk:
- get permissive di fileutils...agar kita bisa bikin --% dan --# sbg daleman dalam sebuah entry
- utk grammar.py agar bisa dipake di filename,f(...), dirname,d(...) dst

kita juga punya __AT utk @ utk nama direktori/file
mending operasi digabungkan di sini dg sanitize_chars.
"""
chars_to_sanitize_in_file_operation = {
    "__DQ": '"',
    "__SQ": "'",
    "__BT": "`",
    "__NL": "\n",
    "__SL": "/",
    "__BS": "\\",
    "__PP": "|",
    "__EQ": "=",
    "__DOLLAR__": "$",
    "__AT__": "@",  # jangan lupa, yg panjang mendahului yg pendek
    "__AT": "@",
    "__PRC__": "%",  # jangan lupa, yg panjang mendahului yg pendek
    "__PRC": "%",  # ini krn %TEMP%,d dianggap sbg %TEMPLATE_SAVE_VAR etc
    "__CL": ":",
    "__SC": ";",
    "__LP": "(",
    "__RP": ")",
    "__LK__": "[",  # jangan lupa, yg panjang mendahului yg pendek
    "__LK": "[",
    "__RK__": "]",  # jangan lupa, yg panjang mendahului yg pendek
    "__RK": "]",
    "__LB": "{",
    "__RB": "}",
    "__LT": "<",
    "__GT": ">",
    "__TAB1": "\t",
    "__TAB2": "\t\t",
    "__TAB3": "\t\t\t",
    "__TAB4": "\t\t\t\t",
    "__SPC1": " ",
    "__SPC2": " " * 2,
    "__SPC3": " " * 3,
    "__SPC4": " " * 4,
    "\\n": "\n",
    "\\t": "\t",
}


def sanitize_chars(content):
    for k, v in chars_to_sanitize_in_file_operation.items():
        content = content.replace(k, v)
    return content


def split_by_pos(strng, sep, pos):
    """
    https://stackoverflow.com/questions/36300158/split-text-after-the-second-occurrence-of-character

    >>> strng = 'some-sample-filename-to-split'
    >>> split(strng, '-', 3)
    ('some-sample-filename', 'to-split')
    >>> split(strng, '-', -4)
    ('some', 'sample-filename-to-split')
    >>> split(strng, '-', 1000)
    ('some-sample-filename-to-split', '')
    >>> split(strng, '-', -1000)
    ('', 'some-sample-filename-to-split')
    """
    strng = strng.split(sep)
    return sep.join(strng[:pos]), sep.join(strng[pos:])
