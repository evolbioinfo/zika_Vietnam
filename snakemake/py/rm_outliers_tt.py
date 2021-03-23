import logging
import re

from Bio.Phylo import NewickIO, write
from Bio.Phylo.NewickIO import StringIO
from pastml.tree import parse_nexus, DATE

ID = '[\\w\\d]+'
NUM = '[+-]?\\d+(?:.\\d+)?(?:[eE][+-]?\\d+)?'
OUTLIER_LINE = 'input date:.+apparent date:'
OUTLIER_LINE_ID = '{id},\s*input date:'.format(id=ID)
NO_SEQ_LINE = 'NO SEQUENCE FOR LEAF:\\s*{id}'.format(id=ID)


def get_ids(file, allowed_diff=1):
    with open(file, 'r') as f:
        for line in f.readlines():
            if re.findall(OUTLIER_LINE, line):
                oline = re.findall(OUTLIER_LINE_ID, line)[0]
                dates = [float(_) for _ in re.findall(NUM, line[line.find('input date:'):])]
                apparent_date = dates[-1]
                print(apparent_date, dates[:-1])
                if (dates[0] - apparent_date > allowed_diff) or (apparent_date - dates[-2] > allowed_diff):
                    yield re.findall(ID, oline)[0]
            else:
                nsline = re.findall(NO_SEQ_LINE, line)
                if nsline:
                    yield re.findall(ID, nsline[0])[-1]


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


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--in_tree', required=True, type=str)
    parser.add_argument('--out_tree_nex', required=True, type=str)
    parser.add_argument('--out_tree_nwk', required=True, type=str)
    parser.add_argument('--allowed_diff', required=False, type=float, default=1)
    parser.add_argument('--ref', required=True, type=str)
    params = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    tree = parse_nexus(params.in_tree)[0]
    ids = set(get_ids(params.ref, params.allowed_diff))
    logging.info('Going to remove {} outliers'.format(len(ids)))
    tree = remove_certain_leaves(tree, lambda tip: tip.name in ids)
    features = [DATE]
    print(tree.write(format_root_node=True, features=[DATE]))
    nwk = tree.write(format_root_node=True, format=3, features=[DATE])
    with open(params.out_tree_nwk, 'w+') as f:
        f.write(nwk)
    write(NewickIO.parse(StringIO(nwk)), params.out_tree_nex, 'nexus')
    with open(params.out_tree_nex, 'r') as f:
        nexus_str = f.read().replace('&&NHX:', '&')
    print(nexus_str)
    for feature in features:
        nexus_str = nexus_str.replace(':{}='.format(feature), ',{}='.format(feature))
    print(nexus_str)
    with open(params.out_tree_nex, 'w') as f:
        f.write(nexus_str)


