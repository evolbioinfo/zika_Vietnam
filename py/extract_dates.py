import pandas as pd


def date2years(d, default='b(0,2019)'):
    if pd.notnull(d):
        first_jan_this_year = pd.datetime(year=d.year, month=1, day=1)
        day_of_this_year = d - first_jan_this_year
        first_jan_next_year = pd.datetime(year=d.year + 1, month=1, day=1)
        days_in_this_year = first_jan_next_year - first_jan_this_year
        return d.year + day_of_this_year / days_in_this_year
    else:
        return default


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--data', required=True, type=str)
    parser.add_argument('--dates', required=True, type=str)
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

    if params.dates:
        with open(params.dates, 'w+') as f:
            f.write('%d\n' % df.shape[0])
        df.to_csv(params.dates, sep='\t', header=False, mode='a')

