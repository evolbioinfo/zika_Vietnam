import logging
from collections import defaultdict

import pandas as pd
from ete3 import Tree


def remove_certain_leaves(tr, to_remove=lambda node: False):
    """
    Removes all the branches leading to leaves identified positively by to_remove function.
    :param tr: the tree of interest (ete3 Tree)
    :param to_remove: a method to check is a leaf should be removed.
    :return: void, modifies the initial tree.
    """
    tips = [tip for tip in tr if to_remove(tip)]
    for tip in tips:
        while tip.is_leaf():
            if tip.is_root():
                return None
            parent = tip.up
            parent.remove_child(tip)
            tip = parent
    while len(tr.children) == 1:
        tr = tr.children[0]
        tr.dist = 0
        tr.up = None
    for parent in tr.traverse('postorder'):
        # If the parent node has only one child now, merge them.
        if len(parent.children) == 1:
            child = parent.children[0]
            child.dist += parent.dist
            grandparent = parent.up
            grandparent.remove_child(parent)
            grandparent.add_child(child)
    return tr


def read_tree(nwk):
    for fmt in (3, 0):
        try:
            return Tree(nwk, format=fmt)
        except:
            continue
    raise ValueError('Could not parse your tree {}'.format(nwk))


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--in_tree', required=True, type=str)
    parser.add_argument('--out_tree', required=True, type=str)
    parser.add_argument('--tab', required=True, type=str)
    params = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    tree = read_tree(params.in_tree)
    df = pd.read_csv(params.tab, sep='\t', index_col=0)

    sg = [t for t in tree if df.loc[t.name, 'country'] == 'Singapore']
    todo = [_ for _ in tree]
    to_remove = set()
    while todo:
        n = todo.pop()
        if n.is_leaf():
            sg = df.loc[n.name, 'country'] == 'Singapore'
        else:
            sg = all(getattr(c, 'SG', False) for c in n.children)
        n.add_feature('SG', sg)
        if sg:
            todo.append(n.up)
        else:
            for c in n.children:
                if getattr(c, 'SG', False) and len(c) > 1:
                    to_remove |= ({_.name for _ in c} - {next(_ for _ in c)})

    logging.info('Going to remove {} SG tips'.format(len(to_remove)))
    remove_certain_leaves(tree, lambda tip: tip.name in to_remove).write(outfile=params.out_tree)


