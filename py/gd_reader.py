import pandas as pd
from Bio import SeqIO

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_fa', required=True, type=str)
    parser.add_argument('--output_fa', required=True, type=str)
    parser.add_argument('--output_data', required=True, type=str)
    parser.add_argument('--gd_data', required=True, type=str, nargs='+')
    parser.add_argument('--input_data', required=True, type=str)
    params = parser.parse_args()

    df = pd.concat([pd.read_csv(data, index_col=0) for data in params.gd_data])
    df = df[df['type support'] == 100]
    df['serotype'], df['genotype'] = df['type'].str.split(' Genotype ', 1).str
    df.drop(labels=['type', 'subtype', 'subtype support', 'type support', 'species-score', 'species', 'assignment'],
            axis=1, inplace=True)
    df['serotype'] = df['serotype'].str.replace('DENV-', '')
    df['genotype'] = df['serotype'] + '.' + df['genotype']
    df['serotype'] = 'DENV' + df['serotype']

    df = df.join(pd.read_csv(params.input_data, index_col=0, sep='\t'), how='inner', rsuffix='.gb')
    df.to_csv(params.output_data, sep='\t', index_label='accession')
    df.index = df.index.map(str)

    SeqIO.write((seq for seq in SeqIO.parse(params.input_fa, "fasta") if seq.id in df.index), params.output_fa, "fasta")
