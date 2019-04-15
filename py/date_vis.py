import matplotlib

import matplotlib.pyplot as plt
import pandas as pd

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--tab', type=str, required=True, nargs='+')
    parser.add_argument('--dates', required=True, type=str)
    parser.add_argument('--rates', required=True, type=str)
    params = parser.parse_args()

    dfs = []
    for tab in params.tab:
        df = pd.read_csv(tab, sep='\t', header=0, index_col=None)
        df.columns = ['type', 'tool', 'clock', 'rate_ci', 'tmrca_ci']
        df['rate'], df['rate_ci'] = df['rate_ci'].str.split(' ', 1).str
        df['rate'] = df['rate'].astype(float)
        df['rate_ci'] = df['rate_ci'].apply(lambda _: [float(_) for _ in _[1:-1].split('-')])
        df['rate_min'] = df['rate_ci'].apply(lambda _: _[0])
        df['rate_Max'] = df['rate_ci'].apply(lambda _: _[1])
        df['rate_m'] = df['rate'] - df['rate_min']
        df['rate_M'] = df['rate_Max'] - df['rate']

        df['tmrca'], df['tmrca_ci'] = df['tmrca_ci'].str.split(' ', 1).str
        df['tmrca'] = df['tmrca'].astype(int)


        def get_mM(ci):
            ci = ci[1:-1]
            sep = ci.find('-', 1)
            return [int(ci[:sep]), int(ci[sep + 1:])]


        df['tmrca_ci'] = df['tmrca_ci'].apply(get_mM)
        df['tmrca_min'] = df['tmrca_ci'].apply(lambda _: _[0])
        df['tmrca_Max'] = df['tmrca_ci'].apply(lambda _: _[1])
        df['tmrca_m'] = df['tmrca'] - df['tmrca_min']
        df['tmrca_M'] = df['tmrca_Max'] - df['tmrca']
        dfs.append(df)

    tool2colour = dict(zip(dfs[0]['tool'].unique(), ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']))

    matplotlib.rcParams.update({'font.size': 8})

    for lbl, file in (('rate', params.rates), ('tmrca', params.dates)):
        plt.clf()
        fig, axs = plt.subplots(2, 1)
        for type, row in zip(dfs[0]['type'].unique(), (0, 1,)):
            x = 0
            y_m, y_M, dt = None, None, None
            x_tics = []
            x_labels = []
            cols = []
            for df, error_col in zip(dfs, ('lightgrey', 'grey')):
                s_df = df[df['type'] == type]
                s_df['x'] = range(x, x + len(s_df))
                x += len(s_df)

                axs[row].set_title(type, fontsize=6)
                colors = [tool2colour[t] for t in s_df['tool'].unique()]
                axs[row].errorbar(x=s_df['x'], y=s_df[lbl], yerr=[s_df[lbl + '_m'], s_df[lbl + '_M']], capsize=2,
                                       linestyle="None", color=error_col, zorder=-1)
                e = axs[row].scatter(x=s_df['x'], y=s_df[lbl], color=colors, s=6, zorder=1)

                mask = (s_df['{}_min'.format(lbl)] > 0) & (s_df['{}_Max'.format(lbl)] < (s_df[lbl] * 10))
                delta = sorted(s_df.loc[mask, '{}_m'.format(lbl)].tolist() + s_df.loc[mask, '{}_M'.format(lbl)].tolist())[-2]
                y_min = min(s_df.loc[mask, '{}_min'.format(lbl)])
                y_max = max(s_df.loc[mask, '{}_Max'.format(lbl)])
                y_min = min(y_min, s_df[lbl].min())
                y_max = max(y_max, s_df[lbl].max())
                if y_m is None:
                    y_m, y_M, dt = y_min, y_max, delta
                else:
                    y_m = min(y_m, y_min)
                    y_M = max(y_M, y_max)
                    dt = max(dt, delta)
                x_tics.extend(s_df['x'].tolist())
                x_labels.extend(s_df['tool'].tolist())
                cols.extend(colors)

            axs[row].set_ylim(y_m - dt, y_M + dt)
            axs[row].set_xticks(x_tics)
            axs[row].set_xticklabels(x_labels)
            for tick in axs[row].yaxis.get_ticklabels():
                tick.set_fontsize(6)
            cit = iter(cols)
            for tick in axs[row].xaxis.get_ticklabels():
                tick.set_fontsize(6)
                tick.set_color(next(cit))
            axs[row].spines['right'].set_visible(False)
            axs[row].spines['top'].set_visible(False)
        fig.autofmt_xdate()
        plt.tight_layout()
        plt.savefig(file, dpi=300, papertype='a5', orientation='landscape')
