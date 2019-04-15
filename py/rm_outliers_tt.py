import logging
import re

from ete3 import Tree

ID = '[\\w\\d]+'
NUM = '[+-]?\\d+(?:.\\d+)?(?:[eE][+-]?\\d+)?'
OUTLIER_LINE = 'input date:.+apparent date:'
OUTLIER_LINE_ID = '{id},\s*input date:'.format(id=ID)
NO_SEQ_LINE = 'NO SEQUENCE FOR LEAF:\\s*{id}'.format(id=ID)


def get_ids(file):
    with open(file, 'r') as f:
        for line in f.readlines():
            if re.findall(OUTLIER_LINE, line):
                oline = re.findall(OUTLIER_LINE_ID, line)[0]
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
    parser.add_argument('--ref', required=True, type=str)
    params = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    tree = read_tree(params.in_tree)
    ids = set(get_ids(params.ref))
    logging.info('Going to remove {} outliers'.format(len(ids)))
    remove_certain_leaves(tree, lambda tip: tip.name in ids).write(outfile=params.out_tree)


