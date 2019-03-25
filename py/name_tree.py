from ete3.parser.newick import write_newick
from ete3 import Tree


def collapse_zero_branches(tree, features_to_be_merged=None):
    num_collapsed = 0

    if features_to_be_merged is None:
        features_to_be_merged = []

    for n in list(tree.traverse('postorder')):
        zero_children = [child for child in n.children if not child.is_leaf() and child.dist <= 0]
        if not zero_children:
            continue
        for feature in features_to_be_merged:
            feature_intersection = set.intersection(*(getattr(child, feature, set()) for child in zero_children)) \
                                   & getattr(n, feature, set())
            if feature_intersection:
                value = feature_intersection
            else:
                value = set.union(*(getattr(child, feature, set()) for child in zero_children)) \
                        | getattr(n, feature, set())
            if value:
                n.add_feature(feature, value)
        for child in zero_children:
            n.remove_child(child)
            for grandchild in child.children:
                n.add_child(grandchild)
        num_collapsed += len(zero_children)
    if num_collapsed:
        print('Collapsed {} internal zero branches.'.format(num_collapsed))


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_tree', required=True, type=str)
    parser.add_argument('--output_tree', required=True, type=str)
    params = parser.parse_args()

    for fmt in range(9):
        try:
            tr = Tree(params.input_tree, format=fmt)
        except:
            pass
    collapse_zero_branches(tr)

    i = 0
    for n in tr.traverse():
        if not n.is_leaf():
            n.name = 'node_{}'.format(i)
            i += 1

    nwk = write_newick(tr, format_root_node=True, format=3)
    with open(params.output_tree, 'w+') as f:
        f.write('%s\n' % nwk)
