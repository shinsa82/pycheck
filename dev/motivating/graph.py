"""
graph.py

From a graph analysis library, which is written in Java.
So it looks like a blackbox function from Python point of view.
"""
from typing import Iterable, Mapping
from pandas import DataFrame
from pycheck import RefinementType

Nodes = RefinementType(
    DataFrame, 'df', lambda df: 'id' in df.columns and df['id'].dtype == int and df.id.is_unique)
Edges = RefinementType(DataFrame, 'df', lambda df: 'source' in df.columns and df.source.dtype ==
                       int and 'target' in df.columns and df.target.dtype == int)
# 同型なグラフをつぶしていい場合とだめな場合
# より簡単な設定で考えるのもよい
# カバレッジ・ループ回数などがばらけるように (Whitebox test っぽくなるが)


def valid_graph(g: tuple[Nodes, Edges]) -> bool:
    nodes, edges = g
    edges.source in nodes.id and edges.target in nodes.id


Graph = RefinementType(tuple[Nodes, Edges], 'g',
                       lambda g: valid_graph(g[0], g[1]))

SDist_Nodes = Nodes

SDist_Edges = RefinementType(
    Edges, 'df', lambda df: 'length' in df.columns and df.length.dtype == int)

SDist_Graph = RefinementType(
    tuple[SDist_Nodes, SDist_Edges], 'g', lambda g: valid_graph(g))
SDist_Ret = RefinementType(Mapping[int, int], 'm', lambda g, target,
                           iterations: 'm is a map of (node_id, sdist) entries of shortest path of target nodes')


def shortest_distance(g: SDist_Graph, target: Iterable[int], iterations: RefinementType(int, 'i', lambda i: i > 0)) -> SDist_Ret:
    ...  # calls the external service computing sdist


# Cycle についても同様。入出力の作り方については2種類あると思っている
# 1. 入力グラフ G をランダムに作って、G の cycle を計算しておいて、関数の返り値とそれが一致するかみる
# 2. ある cycle を持つグラフ G を作って、関数の返り値とそれが一致するかをみる
Cycles_Graph = ...
Cycles_Ret = ...


def cycle_detection(g: Cycles_Graph) -> Cycles_Ret:
    ...

"""
SDist_Graph の generator:

----
def gen_SDist_Graph():
    n ~ gen(SDist_Nodes)
    e ~ gen(SDist_Edges)
    return (n, e)

g ~ gen(SDist_Graph)
assert(valid_graph(g))
----

n ~ gen(SDist_Nodes)
e ~ gen(SDist_Edges)
assert(e.source in n.id and e.target in n.id)

---

c0 ~ gen(posnat)
l0 ~ gen(list[nat])
assume len(l0) == c0
assume unique(l0)
n = Series(l0, name="id")
c1 ~ gen(posnat)
s1 ~ gen(list[nat])
t1 = gen(list[nat])
assume len(s1) == c1
assume len(t1) == c1
e = DataFrame({'source': s1, 'target': t1})
assert(e.source in n.id and e.target in n.id) // ------> 移動すると i ~ gen(nat); assume (i in n.id)

"""