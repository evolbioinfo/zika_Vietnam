import logging
from collections import defaultdict
import re
from ete3 import TreeNode, Tree

import pandas as pd
from pastml import numeric2datetime
from pastml.tree import DATE, read_tree, DATE_CI, annotate_dates, read_nexus, DATE_COMMENT_REGEX, \
    CI_DATE_REGEX_PASTML, CI_DATE_REGEX_LSD, COLUMN_REGEX_PASTML

COUNTRIES = sorted(['Vietnam', 'Thailand', 'Singapore', 'French Polynesia', 'Brazil', 'Colombia', 'Honduras', 'Dominican Republic', 'Puerto Rico', 'Haiti', 'India', 'China'])


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--tree', required=True, type=str)
    parser.add_argument('--tree_acr', required=True, type=str)
    parser.add_argument('--tab', required=True, type=str)
    parser.add_argument('--ntab', required=True, type=str)
    params = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    bs_tree = Tree(params.tree, format=2)
    acr_tree = read_tree(params.tree_acr, columns=['country'])

    c2bs = {}
    c2size = defaultdict(lambda: 0)
    for n in acr_tree.traverse('postorder'):
        if not n.is_root() and getattr(n, 'country') != getattr(n.up, 'country') and not n.is_leaf():
            c = getattr(n, 'country')
            if len(c) == 1:
                c = c.pop()
                if c in COUNTRIES and c2size[c] < len(n):
                    bs_n = bs_tree.get_common_ancestor(*(_.name for _ in n))
                    c2size[c] = len(n)
                    c2bs[c] = bs_n.support

    with open(params.tab, 'w+') as f:
        f.write('country\tbootstrap\n')
        for c in COUNTRIES:
            f.write('{}\t{}\n'.format(c, c2bs[c]))

    with open(params.ntab, 'w+') as f:
        f.write('name\tbootstrap\n')
        for n in acr_tree.traverse('postorder'):
            if not n.is_root() and not n.is_leaf():
                bs_n = bs_tree.get_common_ancestor(*(_.name for _ in n))
                f.write('{}\t{}\n'.format(n.name, bs_n.support))
