import logging
from shutil import copyfile

import pandas as pd

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--trees', required=True, type=str, nargs='+')
    parser.add_argument('--best_tree', required=True, type=str)
    parser.add_argument('--log', required=True, type=str)
    params = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    df = pd.read_csv(params.log, sep='   ', header=None, index_col=0, names=['lh'])
    tree_type = df[df['lh'] == max(df['lh'])].index[0]
    logging.info(tree_type)

    for tree in params.trees:
        if tree_type in tree:
            copyfile(tree, params.best_tree)
            break
