import pandas as pd
import re

NUM = '[+-]?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?'
REXP = 'rate\\s+{num}\\s*\\[\\s*{num}\\s*,\\s*{num}\\s*\\]\\s*,\\s*tMRCA\\s+{num}\\s*\\[\\s*{num}\\s*,\\s*{num}\\s*\\]'.format(num=NUM)

REXP_TT_CI = '--rate:\\s+{num}\\s*\\+/\\-\\s*{num}'.format(num=NUM)
REXP_TT = '--rate:\\s+{num}\\s*$'.format(num=NUM)


def get_info_lsd(file):
    with open(file, 'r') as f:
        for line in f.readlines():
            line = re.findall(REXP, line)
            if line:
                return (float(_) for _ in re.findall(NUM, line[0]))
    return [None] * 6


def get_info_tt(file):
    rate, std = None, None
    with open(file, 'r') as f:
        for line in f.readlines():
            rate_ci = re.findall(REXP_TT_CI, line)
            if rate_ci:
                rate, std = (float(_) for _ in re.findall(NUM, rate_ci[0]))
            else:
                rate_no_ci = re.findall(REXP_TT, line)
                if rate_no_ci:
                    rate = float(re.findall(NUM, rate_no_ci[0])[0])
                    std = 0
    df = pd.read_csv(file.replace('.log', '.dates'), sep='\t', skiprows=[0], index_col=0)
    return [rate, rate - std, rate + std] + (df.iloc[0, -3:].tolist() if len(df.columns) > 2 else (df.iloc[0, -1:].tolist() * 3))


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--logs', required=True, type=str, nargs='+')
    parser.add_argument('--labels', required=True, type=str, nargs='+')
    parser.add_argument('--tab', required=True, type=str)
    parser.add_argument('--type', required=False, type=str, default='tree type')
    params = parser.parse_args()

    with open(params.tab, 'w+') as f:
        f.write('{}\ttool\tclock\trate [x10^-4 subs/site/year] (95% CI)\ttMRCA  (95% CI)\n'.format(params.type))
        for log, label in zip(params.logs, params.labels):
            if 'LSD' in label:
                rate, min_rate, max_rate, tmrca, min_tmrca, max_tmrca = get_info_lsd(log)
                if rate:
                    f.write('{}\tstrict\t{:.2f} ({:.2f}-{:.2f})\t{:.0f} ({:.0f}-{:.0f})\n'
                            .format(label, rate * 1e4, min_rate * 1e4, max_rate * 1e4, tmrca, min_tmrca, max_tmrca))
            elif 'treedater' in label:
                df = pd.read_csv(log, header=0, index_col=None)
                f.write('{}\t{}\t{:.2f} ({:.2f}-{:.2f})\t{:.0f} ({:.0f}-{:.0f})\n'
                        .format(label, df.loc[0, 'clock'], \
                                df.loc[0, "meanRate"] * 1e4, df.loc[0, "meanRate_CI"] * 1e4, df.loc[1, "meanRate_CI"] * 1e4, \
                                df.loc[0, "timeOfMRCA"], df.loc[0, "timeOfMRCA_CI"], df.loc[1, "timeOfMRCA_CI"]))
            elif 'TreeTime' in label:
                rate, min_rate, max_rate, tmrca, min_tmrca, max_tmrca = get_info_tt(log)
                f.write('{}\trelaxed\t{:.2f} ({:.2f}-{:.2f})\t{:.0f} ({:.0f}-{:.0f})\n'
                        .format(label, rate * 1e4, min_rate * 1e4, max_rate * 1e4, tmrca, min_tmrca, max_tmrca))
