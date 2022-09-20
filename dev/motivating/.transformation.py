from numpy import dtype, int64
from pandas import DataFrame, Series, StringDtype

from pycheck.type import Refinement

has_type = ...


def phi(x):
    return 'AccountId' in x.columns and \
        x.AccountId.dtype == int64 and \
        x.AccountId.is_unique and \
        (x.AccountId > 0).all()


print(phi(DataFrame([[1, 2, 3], [4, 5, 6]],
                    columns=['AccountId', 'foo', 'bar'])))
print(phi(DataFrame([['1', 2, 3], ['4', 5, 6]],
                    columns=['AccountId', 'foo', 'bar'])))
print(phi(DataFrame([[1, 2, 3], [4, 5, 6]],
                    columns=['AcountId', 'foo', 'bar'])))
print(phi(DataFrame([[1, 2, 3], [1, 5, 6]],
                    columns=['AccountId', 'foo', 'bar'])))
print(phi(DataFrame([[-1, 2, 3], [4, 5, 6]],
                    columns=['AccountId', 'foo', 'bar'])))

dfi_type = Refinement(
    DataFrame,
    'x',
    phi
)


def phi2(x):
    return 'AccountId' in x.columns and \
        has_type(x.AccountId, Series['{y: int64 | y>0}']) and \
        x.AccountId.is_unique


dfi_type2 = Refinement(DataFrame, 'x', phi2)

"""
x ~ generate(dfi_type)
assume phi(x)

->

m ~ generate(posnat)
n ~ generate(nat)
cols ~ generate(list[str])
assume is_unique(cols)
values = map(cols,                       # <- 生成した変数に関するループ/map
    \c ->
        d ~ generate(dtype)
        s ~ generate(Series[d])
        assume len(s) == n
        return s
)
x = DataFrame(values, cols)              # <- ここで指定した cols が
assume 'AccountId' in x.columns and \    # <- x.colunmsと等しいという知識が必要
       x.AccountId.dtype == int64 and \
       x.AccountId.is_unique and \
       (x.AccountId > 0).all()

->

m ~ generate(posnat)
n ~ generate(nat)
cols ~ generate(list[str])
assume is_unique(cols)
values = map(cols,
    \c ->
        d ~ generate(dtype)
        s ~ generate(Series[d])
        assume len(s) == n
        return s
)
assume 'AccountId' in DataFrame(values, cols).columns and \   
       DataFrame(values, cols).AccountId.dtype == int64 and \
       DataFrame(values, cols).AccountId.is_unique and \
       (DataFrame(values, cols).AccountId > 0).all()
x = DataFrame(values, cols)

上に移動していくと

cols ~ generate(list[str])
assume is_unique(cols)
assume \exists values: 'AccountId' in DataFrame(values, cols).columns

簡約ルールがなりたてば

cols ~ generate(list[str])
assume is_unique(cols)
assume \exists values: 'AccountId' in cols

Useless 変数を削除できて

cols ~ generate(list[str])
assume is_unique(cols)
assume 'AccountId' in cols
assume len(cols) == n

is_unique(a::L) = a not in L && is_unique(L)
2つの条件の構造がことなる場合
木構造
DSL

これを生成することは少ない労力でできる

よって
- データ型 (のコンストラクタ) の状態と成り立つ性質に関する簡約ルール、とくにコンストラクタ引数と性質の関係に関するもの
- ループ/mapもしくはリスト/辞書内包表記に関するルール
"""
