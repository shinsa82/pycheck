# 開発メモ

## Seting up development env

既存の環境削除 (ある場合)

```shell
pipenv --rm
rm Pipenv.lock
```

新環境のセットアップ

```shell
pipenv --python 3.9 # もしくはお好みのバージョン
pipenv install # 必要なはず。もしかしたら前の行が要らないかもしれない
pipenv install --dev
```

更新のチェック

```shell
pipenv update [--outdated] # update コマンドの説明がよくわからないがこれでいいらしい
pipenv clean --dry-run # あるパッケージが必要としていたが、そのバージョンアップに従い必要とされなくなったパッケージが炙り出せてる気がしてる。
```

## Files (整理中)

- [test](../test): pytest でテストするためのテストケース。基本テストが通るように書かれている (つまり、`assert p` が成り立たないことを期待するなら `assert not p` と書くこと)。
- [mypy](../mypy_examples): mypy でテストするためのテストケース。ファイル内に mypy が通るか否かがコメントしてある。

## Top-level Typecheck の対象

Typecheck (`C |- v:t` を判定) するためには callable な term とその type が必要

- 組み込み関数。
- `def` で定義される関数。これは型アノテーションをつけておけば `inspect.signature()` で取得できる。
- `lambda` で定義される関数。これは一般には `Callable` で型をつけるのだが、`lamnda` 式自体につける方法がないので、top-level の型チェックのためには別に与える必要がある。また、`Callable` では検査するのに型が足りないので、`Annotated` で付加することにする。
  - 例: `lambda x, y: x - y` の単純型は `Callable[[int, int], int]` つまり `(int * int) -> int`。つけたい型は少なくとも `(x: int, y: int) -> int`、さらに言えば `(x: int, y: { int | x >= y }) -> { z: int | z >= 0 }` のようにつけたい。
- [TODO] オブジェクトのメソッド。
- [TODO?] オブジェクトのコンストラクタ
- [TODO] Duck typing のための Protocol。このあたりまだよくわかってない。

lambda に限らず、Callable な term の型チェックをする必要がある。高階関数の型は signature はともかく、Callable を付けざるを得ないため。

## Signature の構造

上記 `Signature` のインスタンスは、