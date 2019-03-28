import pandas as pd
from hdx.location.country import Country


def add_loc_info(df):
    df.loc[df['location_details'].str.contains('Puerto Rico') == True, 'country'] = 'Puerto Rico'
    countries = df['country'].unique()

    def get_iso3(country):
        if pd.isna(country):
            return None
        return Country.get_iso3_country_code_fuzzy(country)[0]

    country2iso3 = {_: get_iso3(_) for _ in countries}
    iso32info = {_: Country.get_country_info_from_iso3(_) for _ in country2iso3.values() if _}

    def get_Location(iso3):
        if not iso3:
            return None
        info = iso32info[iso3]
        if 'Oceania' in info['Region Name']:
            return 'Oceania'
        int_region = info['Intermediate Region Name'] if info['Intermediate Region Name'] else info['Sub-region Name']
        if 'Europe' in int_region:
            return 'Europe'
        if 'Africa' in int_region:
            return 'Africa'
        return int_region

    df['country_code'] = df['country'].apply(lambda _: country2iso3[_] if _ in country2iso3 else None)
    df['continent'] = df['country_code'].apply(lambda _: iso32info[_]['Region Name'] if _ in iso32info else None)
    df['sub-region'] = df['country_code'].apply(lambda _: iso32info[_]['Sub-region Name'] if _ in iso32info else None)
    df['region'] = df['country_code'].apply(lambda _: iso32info[_]['Region Name'] if _ in iso32info else None)
    df['int-region'] = df['country_code'].apply(lambda _:
                                                (iso32info[_]['Intermediate Region Name']
                                                 if iso32info[_]['Intermediate Region Name']
                                                 else iso32info[_]['Sub-region Name']) if _ in iso32info else None)
    df['location'] = df['country_code'].apply(get_Location)
    df.loc[df['location_details'].str.contains('Hawaii') == True, 'location'] = 'Oceania'
    return df


def generalise_host(df):
    df['host_type'] = 'monkey'
    df.loc[pd.isna(df['host']), 'host_type'] = None
    df.loc[df['host'].str.contains('Aedes') == True, 'host_type'] = 'mosquito'
    df.loc[df['host'].str.contains('mosquito') == True, 'host_type'] = 'mosquito'
    df.loc[df['host'].str.contains('Armigeres') == True, 'host_type'] = 'mosquito'
    df.loc[df['host'] == 'Homo sapiens', 'host_type'] = 'human'


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_data', required=True, type=str)
    parser.add_argument('--output_data', required=True, type=str)
    params = parser.parse_args()

    df = pd.read_csv(params.input_data, sep='\t', header=0, index_col=0)
    add_loc_info(df)
    generalise_host(df)
    df.to_csv(params.output_data, sep='\t', index_label='accession')
