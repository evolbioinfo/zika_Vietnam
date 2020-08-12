import pandas as pd
from Bio import SeqIO

id2date = {'222_IonXpress_003_rawlib': '24-Jan-2017',  '3015_IonXpress_030_rawlib': '02-Apr-2016',  '3015u_IonXpress_001_rawlib': '02-Apr-2016',  '7040_IonXpress_033_rawlib': '06-Oct-2016',  '7938_IonXpress_048_rawlib': '02-Nov-2016',  '8546_IonXpress_034_rawlib': '17-Nov-2016',  '8607_IonXpress_035_rawlib': '22-Nov-2016',  '8628_IonXpress_066_rawlib': '22-Nov-2016',  '8711_IonXpress_002_rawlib': '22-Nov-2016',  '9453_IonXpress_078_rawlib': '20-Dec-2016',  'IonXpress_003_rawlib': '2016',  'IonXpress_004_rawlib': '2016',  'IonXpress_039_rawlib': '2016',  'IonXpress_040_rawlib': '2016',  'IonXpress_041_rawlib': '2016'}

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_fa', required=True, type=str)
    parser.add_argument('--output_fa', required=True, type=str)
    parser.add_argument('--output_data', required=True, type=str)
    parser.add_argument('--input_Vietnam', required=True, type=str)
    parser.add_argument('--input_data', required=True, type=str)
    params = parser.parse_args()

    df = pd.read_csv(params.input_data, index_col=0, sep='\t')

    recs = []
    for seq in SeqIO.parse(params.input_fa, "fasta"):
        seq.id = seq.id.replace('_', '')
        if seq.id in df.index:
            recs.append(seq)
    for seq in SeqIO.parse(params.input_Vietnam, "fasta"):
        seq.id = seq.id.replace('.basecaller', '')
        recs.append(seq)
        df.loc[seq.id, ['type', 'collection_date', 'country', 'host', 'organism', 'host_details']] = \
            ['Asian', id2date[seq.id], 'Vietnam', 'Homo sapiens', 'Zika virus', 'female']
    df.to_csv(params.output_data, sep='\t', index_label='accession')
    SeqIO.write(recs, params.output_fa, "fasta")