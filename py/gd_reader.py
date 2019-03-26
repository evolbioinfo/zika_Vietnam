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
    df = df[df['type support'] == 1000]
    df.drop(labels=["assignment", "species", "species-score", "type support", "subtype", "subtype support"],
            axis=1, inplace=True)

    df = df.join(pd.read_csv(params.input_data, index_col=0, sep='\t'), how='inner', rsuffix='.gb')
    df.index = df.index.map(str)
    df.index = df.index.map(lambda _: _.replace('_', ''))
    df.to_csv(params.output_data, sep='\t', index_label='accession')
    recs = []
    for seq in SeqIO.parse(params.input_fa, "fasta"):
        seq.id = seq.id.replace('_', '')
        if seq.id in df.index:
            recs.append(seq)
    SeqIO.write(recs, params.output_fa, "fasta")
