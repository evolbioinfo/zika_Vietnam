import xml.etree.ElementTree as ET

"""
DNA, part1 = 1-100, 250-384
DNA, part2 = 101-249\3, 102-249\3
DNA, part3 = 103-249\3
"""

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_xml', required=True, type=str)
    parser.add_argument('--output_partitioning', required=True, type=str)
    parser.add_argument('--tool', required=True, type=str, choices=('raxml', 'iq'))
    parser.add_argument('--level', required=False, type=str, choices=('gene', 'type', 'pos'), default='gene')
    params = parser.parse_args()

    tree = ET.parse(params.input_xml)
    root = tree.getroot()
    model = 'GTR+G6+FO+IO' if 'raxml' == params.tool else 'DNA'

    with open(params.output_partitioning, 'w+') as f:
        if 'gene' == params.level:
            for protein in root:
                attributes = protein.attrib
                gene, start_pos, stop_pos = attributes['abbreviation'], int(attributes['startPosition']), \
                                            (int(attributes['stopPosition']) - 1)
                f.write("{model}, {gene}_12 = {start_1}-{stop}\\3, {start_2}-{stop}\\3\n"
                        "{model}, {gene}_3 = {start_3}-{stop}\\3\n"
                        .format(gene=gene, start_1=start_pos, start_2=start_pos + 1,
                                start_3=start_pos + 2, stop=stop_pos, model=model))
        elif 'type' == params.level:
            structural_str_12 = []
            structural_str_3 = []
            ns_str_12 = []
            ns_str_3 = []
            for protein in root:
                attributes = protein.attrib
                gene, start_pos, stop_pos = attributes['abbreviation'], int(attributes['startPosition']), \
                                            (int(attributes['stopPosition']) - 1)
                if gene in ['C', 'M', 'E']:
                    structural_str_12.append('{start_1}-{stop}\\3, {start_2}-{stop}\\3'.format(
                        start_1=start_pos, start_2=start_pos + 1, stop=stop_pos))
                    structural_str_3.append('{start_3}-{stop}\\3'.format(
                        start_3=start_pos + 2, stop=stop_pos))
                else:
                    ns_str_12.append('{start_1}-{stop}\\3, {start_2}-{stop}\\3'.format(
                        start_1=start_pos, start_2=start_pos + 1, stop=stop_pos))
                    ns_str_3.append('{start_3}-{stop}\\3'.format(
                        start_3=start_pos + 2, stop=stop_pos))
            f.write("{model}, structural_12 = {structural_12}\n"
                    "{model}, structural_3 = {structural_3}\n"
                    "{model}, nonstructural_12 = {nonstructural_12}\n"
                    "{model}, nonstructural_3 = {nonstructural_3}\n"
                    .format(model=model,
                            structural_12=', '.join(structural_str_12), structural_3=', '.join(structural_str_3),
                            nonstructural_12=', '.join(ns_str_12), nonstructural_3=', '.join(ns_str_3)))
        else:
            str_12 = []
            str_3 = []
            for protein in root:
                attributes = protein.attrib
                gene, start_pos, stop_pos = attributes['abbreviation'], int(attributes['startPosition']), \
                                            (int(attributes['stopPosition']) - 1)
                str_12.append('{start_1}-{stop}\\3, {start_2}-{stop}\\3'.format(
                        start_1=start_pos, start_2=start_pos + 1, stop=stop_pos))
                str_3.append('{start_3}-{stop}\\3'.format(
                        start_3=start_pos + 2, stop=stop_pos))
            f.write("{model}, pos_12 = {s_12}\n"
                    "{model}, pos_3 = {s_3}\n"
                    .format(model=model,
                            s_12=', '.join(str_12), s_3=', '.join(str_3)))
