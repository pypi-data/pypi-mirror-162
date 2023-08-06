
# 関数テストツール [ezdbg]
# 【動作確認 / 使用例】

import sys
from sout import sout
from ezpip import load_develop
ezdbg = load_develop("ezdbg", "../", develop_flag = True)

# @ezdbg.rec
# def func(x):
# 	return x ** 2

@ezdbg.test
def func(x):
	return x ** 2

func(17)
