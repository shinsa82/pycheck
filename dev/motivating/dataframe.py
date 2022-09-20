"""
Example(s) of motivating examples using Pandas.
"""
from pandas.api.types import is_string_dtype
from io import StringIO

from numpy import dtype, int64
from pandas import DataFrame, Series, StringDtype, read_csv
from pycheck import ArgsType, RefinementType, spec


def preprocess(df: DataFrame) -> DataFrame:
    """
    Simply typed (and partly typed) version of preprocess.

    preprocesses given DataFrame.

    This method inputs a DataFrame and returns modified one with new columns.
    Input DataFrame should have an AccountId column of type int.
    この AccountId はいくつかのコードが結合されているという想定で、下2桁を捨てた残りが4桁の
    BranchCode として出力の DataFrame に追加される。なお、出力が4桁に満たない場合は 0 で詰められる。
    また、返り値には Id 列が追加される。これは 0 以上の整数値で、一意であることが保証されている。
    """
    print('converting DataFrame...')
    print(f'input shape = {df.shape}')
    df = df.rename_axis('Id')
    s_branch: Series = df.AccountId.floordiv(100).astype(str).str.zfill(4)
    df_out: DataFrame = df.assign(BranchCode=s_branch)
    print(f'converted. output shape = {df_out.shape}')
    return df_out


# for type annotation of preprocess_pycheck
in_type = RefinementType(
    DataFrame,
    'x',
    lambda x:
        'AccountId' in x.columns and
        x.AccountId.dtype == int64 and
        x.AccountId.is_unique and
        (x.AccountId > 0).all()
)

# for type annotation of preprocess_pycheck
ret_type = RefinementType(
    DataFrame,
    'dfo',
    lambda dfo:
        'Id' in dfo.columns and
        'BranchCode' in dfo.columns and
        dfo.Id.dtype == int64 and
        dfo.Id.is_unique and
        (dfo.Id >= 0).all() and
        is_string_dtype(dfo.BranchCode.dtype) and
        (dfo.BranchCode.str.len() == 4).all()
)


@spec(ArgsType(dfi=in_type) >> ret_type)
def preprocess_pycheck(dfi: DataFrame) -> DataFrame:
    """
    preprocesses の PyCheck 対応バージョン.
    """
    print('converting DataFrame...')
    print(f'input shape = {dfi.shape}')
    df = dfi.rename_axis('Id').reset_index()
    s_branch: Series = df.AccountId.floordiv(100).astype('string').str.zfill(4)
    dfo: DataFrame = df.assign(BranchCode=s_branch)
    print(f'converted. output shape = {dfo.shape}')
    return dfo


if __name__ == "__main__":
    df = read_csv(StringIO(
        """Name,AccountId
        Tom,9200
        Jerry,12391"""), dtype={"Name": 'string'})
    print("input:")
    print(df)
    print(df.dtypes)
    print("typecheck:")
    print(in_type.predicate(df))
    print("----")
    print("output:")
    dfo = preprocess_pycheck(df)
    print(dfo)
    print(dfo.dtypes)
    print("typecheck:")
    print(ret_type.predicate(dfo))
