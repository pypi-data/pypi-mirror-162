# ezdbg

下の方に日本語の説明があります

## Overview
- easy func debug tool
- description is under construction

## Usage
- recording (record arguments of the target function)
```python
import ezdbg

@ezdbg.rec
def func(x):
	return x ** 2

func(17)
```

- unit test of the function (Only the function is executed.)
```python
import ezdbg

@ezdbg.test	# 【！】REWRITE HERE
def func(x):
	return x ** 2

func(17)
```

## 概要
- python関数を簡単にデバッグできるツール
- 説明は執筆中です

## 使い方
- 記録時 (関数の引数を記録)
```python
import ezdbg

@ezdbg.rec
def func(x):
	return x ** 2

func(17)
```

- 関数単体テスト時 (その関数のみが実行される)
```python
import ezdbg

@ezdbg.test	# 【！】ここを書き換える
def func(x):
	return x ** 2

func(17)
```
