import re

from matplotlib.pyplot import boxplot, savefig, show, plot

NUM = '[+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?'
REXP = 'rate\\s+{num}\\s*\\[\\s*{num}\\s*,\\s*{num}\\s*\\]'.format(num=NUM)


def get_tmrcas(file):
    with open(file, 'r') as f:
        for line in f.readlines():
            line = re.findall(REXP, line)
            if line:
                return (float(_) for _ in re.findall(NUM, line[0]))
    return None, None, None


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--logs', required=True, type=str, nargs='+')
    parser.add_argument('--real_log', required=True, type=str)
    parser.add_argument('--pdf', required=True, type=str)
    params = parser.parse_args()

    x = 0
    tmrca, min_tmrca, max_tmrca = get_tmrcas(params.real_log)
    plot([x, x], [min_tmrca, max_tmrca], 'r')
    plot([x], [tmrca], 'ro')
    for file in params.logs:
        x += .1
        tmrca, min_tmrca, max_tmrca = get_tmrcas(file)
        plot([x, x], [min_tmrca, max_tmrca], 'b')
        plot([x], [tmrca], 'bo')
    savefig(params.pdf)
