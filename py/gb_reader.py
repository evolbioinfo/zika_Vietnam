import pandas as pd
import re
from Bio import SeqIO, Entrez


def fetch_metadata_from_entrez(ids):
    Entrez.email = 'anna.zhukova@pasteur.fr'
    handle = Entrez.efetch('nuccore', id=ids, retmode='xml')
    response = Entrez.read(handle)

    df = pd.DataFrame(index=ids, columns=['collection_date', 'country', 'host', 'mol_type',
                                          'strain', 'pubmed'])

    for entry in response:
        accession = entry['GBSeq_primary-accession']
        for source in (_ for _ in entry['GBSeq_feature-table'] if _['GBFeature_key'] == 'source'):
            for qual in source['GBFeature_quals']:
                if qual['GBQualifier_name'] in df.columns:
                    df.loc[accession, qual['GBQualifier_name']] = qual['GBQualifier_value']

        if 'GBSeq_organism' in entry:
            organism = entry['GBSeq_organism']
            if not pd.isnull(organism):
                df.loc[accession, 'organism'] = organism

        pubmed = []
        if 'GBSeq_references' in entry:
            for ref in entry['GBSeq_references']:
                if 'GBReference_pubmed' in ref:
                    pubmed.append(ref['GBReference_pubmed'])
        df.loc[accession, 'pubmed'] = ','.join(pubmed)
    # df = df[~pd.isna(df['collection_date']) & ~pd.isna(df['country'])]
    df['country'], df['location_details'] = df['country'].str.replace(': ', ':').str.split(':', 1).str
    df['host'], df['host_details'] = df['host'].str.replace('; ', ';').str.split(';', 1).str
    df['host'] = df['host'].str.replace(r'\s\([\w]+\)', '')
    return df


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_fa', required=True, type=str)
    parser.add_argument('--output_fa', required=True, type=str)
    parser.add_argument('--output_data', required=True, type=str)
    parser.add_argument('--output_chunks', type=str, nargs='*')
    params = parser.parse_args()

    recs = list(SeqIO.parse(params.input_fa, "fasta"))
    for rec in recs:
        new_id = re.search(r'^lcl\|[\w]+', rec.id)
        if new_id:
            rec.id = new_id[0].replace('lcl|', '')
        rec.description = ''
    df = fetch_metadata_from_entrez([_.id for _ in recs])
    df.to_csv(params.output_data, sep='\t', index_label='accession')
    records = [seq for seq in recs if seq.id in df.index]
    SeqIO.write(records, params.output_fa, "fasta")

