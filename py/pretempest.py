import pandas as pd
from ete3 import Tree


def date2years(d, default=''):
    if pd.notnull(d):
        return d.year
    else:
        return default


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--data', required=True, type=str)
    parser.add_argument('--input_tree', required=True, type=str)
    parser.add_argument('--output_tree', required=True, type=str)
    parser.add_argument('--date_col', required=True, type=str)
    parser.add_argument('--genotype_col', required=True, type=str)
    params = parser.parse_args()

    df = pd.read_csv(params.data, index_col=0, sep='\t')[[params.date_col, params.genotype_col]]
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

    tree = Tree(params.input_tree)
    for _ in tree:
        _.name = '{}_{}_{}'.format(_.name, str(df.loc[_.name, params.genotype_col]).split(' ')[0], 
                                   df.loc[_.name, params.date_col])
    tree.write(outfile=params.output_tree)

