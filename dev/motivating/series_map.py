"""
higher-order arguments.
"""
from collections.abc import Mapping
from inspect import signature
from typing import Callable, Literal, Optional, TypeVar, overload

from pandas import DataFrame, Series, notnull
from pycheck import check
from numpy import nan
from pycheck.type import Function, Refinement

T = int  # instantiated type variable
U = int  # instantiated type variable


def implies(p: bool, q: bool) -> bool:
    return not p or q

# Series.map() の型検査: Series の各要素に関数を適用したり、それらを置き換えたりするメソッド
# 置き換え方法/置き換え先 には3種類選べる: 関数、dict、Series
# 置き換え元が NaN を含む場合の処理を na_action で指定する; None か 'ignore'
#
# Series および DataFrame が NaN を含むかどうかは重要
#   na_action=='ignore' かつ定義域側が NaN を含めば、(そのままスルーされるので) 結果は NaN を含む
# とは書ける

ret_type = Refinement(Series, 's',
                      lambda s, self, na_action: s.dtype == U and implies(na_action == 'ignore' and self.hasnans, s.hasnans))

#   もし arg の値域が NaN を含まなければ、結果にも NaN を含まない
# と書きたい
# 1) arg が Mapping や Series のときには書ける
# 2) arg が関数の場合には f: int -> int , f: int -> int + None // 引数をうまく網羅的に生成する。関数の分布とは
# 関数の refinement check をできるだけ中の方に入れるなどする
# forall がないと書けない


@overload
def series_map(
        self: Refinement(Series, 's', lambda s: s.dtype == T),
        arg: Function([T], U),
        na_action: Optional[Literal['ignore']]) -> ret_type:
    ...


@overload
def series_map(
        self: Refinement(Series, 's', lambda s: s.dtype == T),
        arg: Mapping[T, U],
        na_action: Optional[Literal['ignore']]) -> ret_type:
    ...


def series_map(
        self: Refinement(Series, 's', lambda s: s.dtype == T),
        arg: Refinement(Series, 's', lambda s: s.dtype == U),
        na_action: Optional[Literal['ignore']] = None) -> ret_type:
    return self.map(arg, na_action=na_action)

# 結構振る舞いが複雑 (NaN 値同士は比較できない、などいろいろな隠れた spec があるので)
if __name__ == '__main__':
    s1: Series = Series([2, 3, 5, 7, None])  # <- NaN 値を持つ
    print(f"in dtype = {s1.dtype}")
    print(s1)

    inc: Callable[[int], int] = lambda n: n + 1 if notnull(n) else -1
    s2: Series = series_map(s1, inc, 'ignore')
    print(f"out dtype = {s2.dtype}")
    print(s2)

    s3: Series = series_map(s1, inc)
    print(s3)

    d = {2: 2.1, 3: 3.1, 5: 5.1, 7: 7.1, nan: -1.0}
    s4: Series = series_map(s1, d, na_action='ignore')
    print(s4)
    s5: Series = series_map(s1, d)
    print(s5)

    ser = Series([9, 11, 13, 17, -1], index=[2, 3, 5, 7, nan])
    s6: Series = series_map(s1, ser, na_action='ignore') # ignore 指定が無視されている?
    print(s6)
    s7: Series = series_map(s1, ser)
    print(s7)

    # なお、メソッドを関数方式で呼べるかというと呼べる
    s8: Series = Series.map(s1, inc, 'ignore')
    print(s8)

    # check(series_map)
    # print(signature(series_map))
