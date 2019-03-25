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
    for node in tips:
        if node.is_root():
            return None
        parent = node.up
        parent.remove_child(node)
        # If the parent node has only one child now, merge them.
        if len(parent.children) == 1:
            brother = parent.children[0]
            brother.dist += parent.dist
            if parent.is_root():
                brother.up = None
                tr = brother
            else:
                grandparent = parent.up
                grandparent.remove_child(parent)
                grandparent.add_child(brother)
    return tr


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--data', required=True, type=str)
    parser.add_argument('--input_tree', required=True, type=str)
    parser.add_argument('--output_tree', required=True, type=str)
    params = parser.parse_args()

    df = pd.read_csv(params.data, index_col=0, sep='\t')

    # calculate interquartile range
    q25, q75 = pd.np.percentile(df['residual'], 25), pd.np.percentile(df['residual'], 75)
    iqr = q75 - q25
    # calculate the outlier cutoff
    cut_off = iqr * 1.5
    lower, upper = q25 - cut_off, q75 + cut_off
    old_len = len(df)
    df = df[(df['residual'] > lower) & (df['residual'] < upper)]
    df.index = df.index.map(str)
    print('Removed {} outliers.'.format(old_len - len(df)))

    tree = None
    for fmt in range(10):
        try:
            tree = Tree(params.input_tree, format=fmt)
            break
        except:
            continue
    for _ in tree:
        _.name = _.name.replace("'", '')
    tree = remove_certain_leaves(tree, lambda tip: tip.name not in df.index)

    for _ in tree:
        _.name = _.name.split('_')[0]
    tree.write(outfile=params.output_tree)

