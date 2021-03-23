import logging
from collections import defaultdict

import pandas as pd
from Bio.Phylo import NewickIO, write
from Bio.Phylo.NewickIO import StringIO
from pastml.tree import DATE, DATE_CI, remove_certain_leaves, annotate_dates, parse_nexus

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--in_tree', required=True, type=str)
    parser.add_argument('--out_tree', required=True, type=str)
    parser.add_argument('--threshold', required=False, type=int, default=10)
    parser.add_argument('--tab', required=True, type=str)
    params = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    tree = parse_nexus(params.in_tree)[0]
    annotate_dates([tree])
    for i, n in enumerate(tree.traverse('preorder')):
        if n.is_root():
            n.name = 'root'
        elif not n.is_leaf():
            n.name = 'n{}'.format(i)
    tree_ids = [_.name for _ in tree]
    df = pd.read_csv(params.tab, sep='\t', index_col=0)
    df = df.loc[df.index.isin(tree_ids), :]
    cdf = df[['country', 'host']].groupby(['country']).count().to_dict()['host']
    for c, n in cdf.items():
        print(c, n)

    c2ids = defaultdict(set)
    for t in tree:
        if t.name in df.index:
            c2ids[df.loc[t.name, 'country']].add(t.name)
    to_keep = set()
    for c, ids in c2ids.items():
        if not pd.isna(c):
            if len(ids) <= params.threshold:
                to_keep |= ids
            else:
                to_keep |= set(pd.np.random.choice(list(ids), size=params.threshold, replace=False))

    tree = remove_certain_leaves(tree, lambda _: _.name not in to_keep)
    features = [DATE, DATE_CI]
    nwk = tree.write(format_root_node=True, features=features, format=3)
    write(NewickIO.parse(StringIO(nwk)), params.out_tree, 'nexus')
    with open(params.out_tree, 'r') as f:
        nexus_str = f.read().replace('&&NHX:', '&')
    for feature in features:
        nexus_str = nexus_str.replace(':{}='.format(feature), ',{}='.format(feature))
    with open(params.out_tree, 'w') as f:
        f.write(nexus_str)
