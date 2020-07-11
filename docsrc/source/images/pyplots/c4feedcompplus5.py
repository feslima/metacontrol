import pandas as pd
import matplotlib.pyplot as plt


DIST = r"Disturbance: Increase of 5% in the feed composition."
DATFOLDER = "dat_source/"
DATFILES = [
    "ic4_+5_NC4_Feed_(69_to_74)_0.dat",
    "ic4_+5_NC4_Feed_(69_to_74)_1.dat",
    "ic4_+5_NC4_Feed_(69_to_74)_2.dat",
]

rows = len(DATFILES)
cols = 1

title_label = [
    ('Stage 32 Temperature - DIB', r'$c^{t32}_{1}$ (°C)'),
    ('Stage 14 Temperature - Purge', r'$c^{t14}_{2}$ (°C)'),
    ('IC5 Distillate composition', r'$ic^{d2}_{5}$ (°C)'),
]
y_label = ['PV', 'PV', 'PV']
y_limits = [
    (56, 58),
    (48, 52),
    (0.002, 0.016)
]

height = 10.0  # inches
aspect_ratio = 4 / 3
width = aspect_ratio * height


def plot_graph(DIST: str, DATFOLDER: str, DATFILES: list,
               rows: int, cols: int, y_labels: list, y_limits: list,
               title_label: list, width: float, height: float):

    fig, axs = plt.subplots(rows, cols)
    fig.set_size_inches(width, height)

    for i, filename in enumerate(DATFILES):
        ax = axs[i]
        ymin, ymax = y_limits[i]
        title, ylabel = title_label[i]

        title = DIST + '\n' + title

        df = pd.read_csv(DATFOLDER + filename, sep='\t')

        time = df['Time']
        pv = df[y_labels[i]]

        ax.plot(time, pv, color='blue')
        ax.grid(which='both')
        ax.set_title(title)
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel(ylabel)

        if ymin is not None and ymax is not None:
            ax.set_ylim(ymin, ymax)

    plt.tight_layout()
    plt.show()


plot_graph(DIST, DATFOLDER, DATFILES, rows, cols, y_label, y_limits,
           title_label, width, height)
