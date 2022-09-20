"""
Typing Dask library
"""
from typing import Any, Iterable, Literal, Mapping, TypeVar, Union, overload

from pandas import DataFrame
from pycheck.type import Function, Refinement

# Dask は Pandas ラッパの並列・遅延計算ライブラリ
# 実際に計算結果を見る前に結果の性質を知りたい
import dask.dataframe as dd
from dask.delayed import Delayed

T = TypeVar('T', bound=DataFrame)

# how to create delayed DataFrame
df: DataFrame = ...
ddf: dd.DataFrame = df.from_pandas(df)


def compute(ddf: dd.DataFrame) -> Refinement(DataFrame, 'df', lambda df, ddf: df.dtypes == ddf.dtypes):
    ...


def p(d: Delayed, ddf: dd.DataFrame) -> bool:
    df = d.compute()
    return isinstance(df, DataFrame) and df.dtypes == ddf.dtypes


def to_delayed(ddf: dd.DataFrame) -> Iterable[Refinement(Delayed, 'd', p)]:
    return ddf.to_delayed()


U = TypeVar('U')
A = TypeVar('A', bound=tuple)
K = TypeVar('K', Mapping[str, Any])


def return_type(f) -> type:
    """
    ある関数 f の型のうち、返り値部分を返す、という操作が必要。
    もしくは f の型ヒントの返り値部分、でもいい。
    (類似の関数が必要であることは関数型が特殊な Python では問題になっていて、新しい記法が導入予定)
    もしくは型変数を使って書いておいて、型検査時に instantiate できるようにする?
    """
    pass


@ overload
# dd.DataFrame.apply には現在 meta 変数が必要。これは apply の結果の型 (列シグネチャ) を明示する必要がある。
# 型があればこれはいらないはず
def ddf_apply(
    # func は DataFrame の各行を受け取って、新しい各行を返す関数。
    # この引数の型が self の列の型と、args の型と、kwargs の型に依存する; 引数の並び順と異なる。
    # 順になるように、無理やり書くことはできるが不自然
    # 宣言における引数順は無視して、トポロジカルソートできればOKとする?
    self: Refinement(dd.DataFrame, 'ddf', lambda ddf: ...),
    func: Function('ddf.dtypes と、type(args) と、type(kwargs) を並べた型', Refinement(U, 'u', 'u is non-iterable type')),
    axis: Literal[1, 'columns'],
    meta: ...
    broadcast,
    raw,
    reduce,
    args: tuple,
    result_type,
    **kwargs: K
) -> Refinement(dd.Series, 'ss', lambda ss, func: ss.dtype == return_type(func)):
    ...


@overload
# 理想はこうか
# def ddf_apply(
#     # func は DataFrame の各行を受け取って、新しい各行を返す関数。
#     # この引数の型が self の列の型と、args の型と、kwargs の型に依存する; 引数の並び順と異なる。
#     # 順になるように、無理やり書くことはできるが不自然
#     # 宣言における引数順は無視して、トポロジカルソートできればOKとする?
#     self: Refinement(dd.DataFrame, 'ddf', lambda ddf: ...),
#     func: Function('ddf.dtypes と、type(args) と、type(kwargs) を並べた型', U),
#     axis: Literal[1, 'columns'],
#     broadcast,
#     raw,
#     reduce,
#     args: tuple,
#         result_type, **kwargs: K) -> Refinement(dd.Series, 'ss', lambda ss, func: ss.dtype == U):
#     ...
# としておいて、型検査時は check(ddf_apply, {U: int}) みたいな
@ overload
# dd.DataFrame.apply には現在 meta 変数が必要。これは apply の結果の型 (列シグネチャ) を明示する必要がある。
# 型があればこれはいらないはず
def ddf_apply(
    # func は DataFrame の各行を受け取って、新しい各行を返す関数。
    # この引数の型が self の列の型と、args の型と、kwargs の型に依存する; 引数の並び順と異なる。
    # 順になるように、無理やり書くことはできるが不自然
    # 宣言における引数順は無視して、トポロジカルソートできればOKとする?
    self: Refinement(dd.DataFrame, 'ddf', lambda ddf: ...),
    func: Function('ddf.dtypes と、type(args) と、type(kwargs) を並べた型', Refinement(U, 'u', 'u is iterable type')),
    axis: Literal[1, 'columns'],
    broadcast,
    raw,
    reduce,
    args: tuple,
    result_type,
    **kwargs: K
) -> Refinement(dd.DataFrame, 'ddf', lambda ddf, func: ddf.dtypes == return_type(func)):
    ...
