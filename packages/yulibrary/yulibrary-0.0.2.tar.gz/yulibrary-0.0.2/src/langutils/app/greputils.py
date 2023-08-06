import os, re
from .utils import (
	env_exist, env_get, env_int, perintahsp_outerr_as_shell, platform
)
from .dirutils import normy

GREP_COMMAND = 'grep'
if platform() in ['win32', 'windows']:
	# GREP_COMMAND = 'wsl grep'
	GREP_COMMAND = 'C:/work/usr/local/wbin/grep.exe'
	if env_exist('ULIBPY_GREP_UTIL_LOCATION'):
		GREP_COMMAND = env_get('ULIBPY_GREP_UTIL_LOCATION')
	else:
		print(f"set ULIBPY_GREP_UTIL_LOCATION to location of grep.exe or use {GREP_COMMAND} as current setting")


def curdir_grep(basedir, pattern, case_sensitive=False, context=0, before=0, after=0, capture=False, no_color=False):
	context_opts = ''
	if before:
		context_opts = f"-B {before}"
	if after:
		context_opts += f"{' ' if context_opts else ''}-A {after}"
	if context:
		context_opts = f"-C {context}"
	# print('A:', after, 'B:', before, 'C:', context, '=>', context_opts)
	basedir = normy(basedir)
	# basedir = basedir.replace('\\', '/')
	print(f'''[greputils]
	basedir = {basedir}
	''')
	skip_binary = "-I"
	color_opt = '' if no_color else ' --color=always -s'
	main_opts = f"-n {skip_binary}{color_opt}" # -s silent jk grep dir
	if ' ' in basedir:
		basedir = f'"{basedir}"'
	if env_int('ULIBPY_WMC_CASESENSITIVE_GREP'):
		case_sensitive = True
	all_opts = f'{GREP_COMMAND} {"" if case_sensitive else "-i"} {main_opts} {context_opts} -e "{pattern}" {basedir}/*'
	# os.system('pwd')
	# print('curdir {GREP_COMMAND}', pattern, '->', all_opts)  
	if capture:
		return perintahsp_outerr_as_shell(all_opts)
	else:
		os.system(all_opts)
	return None


def system_grep(basedir,
	pattern,
	case_sensitive=False,
	context=0,
	before=0,
	after=0,
	capture=False,
	no_color=False):
	context_opts = ''
	if before:
		context_opts = f"-B {before}"
	if after:
		context_opts += f"{' ' if context_opts else ''}-A {after}"
	if context:
		context_opts = f"-C {context}"
	# print('A:', after, 'B:', before, 'C:', context, '=>', context_opts)
	basedir = normy(basedir)
	# basedir = basedir.replace('\\', '/')
	print(f'''[greputils]
	basedir = {basedir}
	''')
	skip_binary = "-I"
	color_opt = '' if no_color else ' --color=always'
	if platform() in ['win32', 'windows', 'desktop']:
		color_opt = ''
	main_opts = f"-n {skip_binary}{color_opt} -r"
	if ' ' in basedir:
		basedir = f'"{basedir}"'
	if env_int('ULIBPY_WMC_CASESENSITIVE_GREP'):
		case_sensitive = True
	all_opts = f'{GREP_COMMAND} {"" if case_sensitive else "-i"} {main_opts} {context_opts} -e "{pattern}" {basedir}'
	# print(f'{GREP_COMMAND} system:', all_opts)
	if capture:
		return perintahsp_outerr_as_shell(all_opts)
	else:
		os.system(all_opts)
	return None


def system_grep_limitchars(basedir,
	pattern, 
	limit=10, 
	case_sensitive=False, 
	capture=False,
	no_color=False):
	"""
	N=10; grep -roP ".{0,$N}\Wactor.{0,$N}" .

	N=limit; grep -roP ".{0,$N}" +pattern+ ".{0,$N}" basedir
	-P adlh perl style dg .{0,$bilangan}

	di sini kita gunakan
	grep -i -I --color=always -ro -P ".{0,n}pattern.{0,n}" basedir
	"""
	skip_binary = "-I"
	color_opt = '' if no_color else ' --color=always'
	if platform() in ['win32', 'windows', 'desktop']:
		color_opt = ''
	main_opts = f"{skip_binary}{color_opt} -ro"
	# main_opts = f"{skip_binary} --color=always -ro"
	if ' ' in basedir:
		basedir = f'"{basedir}"'
	if env_int('ULIBPY_WMC_CASESENSITIVE_GREP'):
		case_sensitive = True
	all_opts = f'{GREP_COMMAND} {"" if case_sensitive else "-i"} {main_opts} -P ".{{0,{limit}}}{pattern}.{{0,{limit}}}" {basedir}'
	# print(f'{GREP_COMMAND} limit:', all_opts)
	if capture:
		return perintahsp_outerr_as_shell(all_opts)
	else:
		os.system(all_opts)
	return None


def system_find(basedir, pattern, opts=None, capture=False):
	"""
	kita tambah sendiri *cari*
	"""
	case_sensitive = 'name'
	if env_int('ULIBPY_WMC_CASESENSITIVE_GREP'):
		case_sensitive = 'iname'
	all_opts = f'find {basedir} -{case_sensitive} "*{pattern}*"'
	if capture:
		return perintahsp_outerr_as_shell(all_opts)
	else:
		os.system(all_opts)
	return None


def pattern_search(filepath, code):
	"""
	"""
	from .fileutils import file_lines
	all_lines = file_lines(filepath)

	# antipatterns = [item.replace('-','',1) for item in code if re.match(r'^-[\w\d]+', item)]
	# patterns = [item for item in code if not re.match(r'^-[\w\d]+', item)]

	# pre_selected = filter(lambda baris: all(
	# 	[item.lower() in baris.lower() for item in patterns]), all_lines)
	# selected = filter(lambda baris: all(
	# 	[item.lower() not in baris.lower() for item in antipatterns]), pre_selected)
	# selected = list(selected)
	# selected = '\n'.join(selected)
	# return selected
	return pattern_search_list(all_lines, code)


def pattern_search_list(all_lines, code, aslist=False):
	"""
	search code yg berisi + dan - dari dalam list all_lines
	[satu_pat1,dua_pat2,tiga_pat3,empat_pat4,lima_pat5]
	+pat1
	-pat2
	+pat3
	-pat4
	"""
	if isinstance(code, str):
		code = [item.strip() for item in code.split()]
	
	# code di sini sudah jadi list of search terms
	antipatterns = [item.replace('-','',1) for item in code if re.match(r'^-[\w\d]+', item)]
	patterns = [item for item in code if not re.match(r'^-[\w\d]+', item)]

	# step 1: ambil dulu yg patterns (+) dari haystack all_lines
	pre_selected = filter(lambda baris: all(
		[item.lower() in baris.lower() for item in patterns]), all_lines)
	# step 2: filter out yg anti (-)
	selected = filter(lambda baris: all(
		[item.lower() not in baris.lower() for item in antipatterns]), pre_selected)
	# filter -> list
	selected = list(selected)
	# return selected as list atau stringified
	if aslist:
		return selected
	selected = '\n'.join(selected)
	return selected


def pattern_search_string(content, code, aslist=False):
	"""
	search code yg berisi + dan - dari dalam string content terpisah spasi
	"""
	return pattern_search_list(content.splitlines(), code, aslist=aslist)

