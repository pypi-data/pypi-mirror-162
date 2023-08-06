
# 関数テストツール [ezdbg]

import sys
import fies
from sout import sout

# 引数記録
def rec(func):
	def modified_func(*ls_args, **kw_args):
		# 引数を保存
		fies["_ezdbg_dump.pickle"] = {
			"ls_args": ls_args,
			"kw_args": kw_args,
		}
		sys.exit()
		# 元の関数を呼ぶ
		return func(*ls_args, **kw_args)
	# 引数を記録するようにした関数
	return modified_func

# テスター
def test(func):
	# 引数を保存
	args = fies["_ezdbg_dump.pickle"]
	ls_args = args["ls_args"]
	kw_args = args["kw_args"]
	# 引数のレビュー
	print("args:")
	sout(args)
	# 元の関数を呼ぶ
	result = func(*ls_args, **kw_args)
	# 結果のレビュー
	print("return value:")
	sout(result)
	sys.exit()
