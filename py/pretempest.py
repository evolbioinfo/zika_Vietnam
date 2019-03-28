import pandas as pd
from ete3 import Tree


def date2years(d, default=None):
    if pd.notnull(d):
        first_jan_this_year = pd.datetime(year=d.year, month=1, day=1)
        day_of_this_year = d - first_jan_this_year
        first_jan_next_year = pd.datetime(year=d.year + 1, month=1, day=1)
        days_in_this_year = first_jan_next_year - first_jan_this_year
        return d.year + day_of_this_year / days_in_this_year
    else:
        return default


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
    tr.dist = 0
    return tr


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--data', required=True, type=str)
    parser.add_argument('--input_tree', required=True, type=str)
    parser.add_argument('--output_tree', required=True, type=str)
    parser.add_argument('--date_col', required=True, type=str)
    params = parser.parse_args()

    df = pd.read_csv(params.data, index_col=0, sep='\t')[[params.date_col]]
    try:
        df[params.date_col] = pd.to_datetime(df[params.date_col], format='%Y')
    except ValueError:
        try:
            df[params.date_col] = pd.to_datetime(df[params.date_col], infer_datetime_format=True)
        except ValueError:
            try:
                df[params.date_col] = pd.to_datetime(df[params.date_col], format='%Y.0')
            except ValueError:
                raise ValueError('Could not infer the date format for column "{}", please check it.'
                                 .format(params.date_col))
    df[params.date_col] = df[params.date_col].apply(lambda d: date2years(d))
    df.index = df.index.map(str)

    print(df.head())

    tree = remove_certain_leaves(Tree(params.input_tree), lambda _: pd.isna(df.loc[_.name, params.date_col]))
    for _ in tree:
        _.name = '{}_{}'.format(_.name, df.loc[_.name, params.date_col])
    tree.write(outfile=params.output_tree)

