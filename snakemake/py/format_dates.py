import logging
from collections import defaultdict
import re
from ete3 import TreeNode

import pandas as pd
from pastml import numeric2datetime
from pastml.tree import DATE, read_tree, DATE_CI, annotate_dates, read_nexus, DATE_COMMENT_REGEX, \
    CI_DATE_REGEX_PASTML, CI_DATE_REGEX_LSD, COLUMN_REGEX_PASTML, parse_nexus

COUNTRIES = sorted(['Vietnam', 'Thailand', 'Singapore', 'French Polynesia', 'Brazil', 'Colombia', 'Honduras', 'Dominican Republic', 'Puerto Rico', 'Haiti', 'India', 'China'])

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--tree_tt_nex', required=True, type=str)
    parser.add_argument('--dates_tt', required=True, type=str)
    parser.add_argument('--tree_tt_acr', required=True, type=str)
    parser.add_argument('--tree_lsd2_nex', required=True, type=str)
    parser.add_argument('--tree_lsd2_acr', required=True, type=str)
    parser.add_argument('--tab', required=True, type=str)
    params = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    timetree_lsd2 = parse_nexus(params.tree_lsd2_nex)[0]
    annotate_dates([timetree_lsd2])
    timetree_tt = parse_nexus(params.tree_tt_nex)[0]
    annotate_dates([timetree_tt])

    acrtree_lsd2 = read_tree(params.tree_lsd2_acr, columns=['country'])
    acrtree_tt = read_tree(params.tree_tt_acr, columns=['country'])

    date_df = pd.read_csv(params.dates_tt, sep='\t', index_col=0, skiprows=[0])[['numeric date', 'lower bound', 'upper bound']]


    get_ci_lsd2 = lambda _: getattr(_, DATE_CI)
    get_ci_tt = lambda _: date_df.loc[_.name, ['lower bound', 'upper bound']]

    def get_dates(acrtree, timetree, get_ci):
        c2dates = {}
        c2size = defaultdict(lambda: 0)
        for n in acrtree.traverse('postorder'):
            if not n.is_root() and getattr(n, 'country') != getattr(n.up, 'country') and not n.is_leaf():
                c = getattr(n, 'country')
                if len(c) == 1:
                    c = c.pop()
                    if c in COUNTRIES and c2size[c] < len(n):
                        time_n = timetree.get_common_ancestor(*(_.name for _ in n))
                        c2size[c] = len(n)
                        ci_l, ci_u = get_ci(time_n)
                        c2dates[c] = [getattr(time_n, DATE), ci_l, ci_u]
                        while n.up and c in getattr(n.up, 'country'):
                            c2dates[c][1] = get_ci(time_n.up)[0]
                            n = n.up
                            time_n = time_n.up
        return c2dates

    country2tt_dates = get_dates(acrtree_tt, timetree_tt, get_ci_tt)
    country2lsd2_dates = get_dates(acrtree_lsd2, timetree_lsd2, get_ci_lsd2)

    with open(params.tab, 'w+') as f:
        f.write('country\tLSD2 date [CI]\tTreeTime date [CI]\n')
        for c in COUNTRIES:
            f.write('{}\t{} [{}-{}]\t{} [{}-{}]\n'
                    .format(c,
                            *[numeric2datetime(_).strftime("%d %b %Y") for _ in country2lsd2_dates[c]],
                            *[numeric2datetime(_).strftime("%d %b %Y") for _ in country2tt_dates[c]]))


