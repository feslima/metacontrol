import pandas as pd
import matplotlib.pyplot as plt


DIST = r"Disturbance: Decrease of 5% in the feed flowrate."
DATFOLDER = "dat_source/"
DATFILES = [
    "indirect_c3_420_to_399_kmol_(-5)_feed_0.dat",
    "indirect_c3_420_to_399_kmol_(-5)_feed_1.dat",
    "indirect_c3_420_to_399_kmol_(-5)_feed_2.dat",
]

rows = len(DATFILES)
cols = 1

title_label = [
    (r'$Cv_1 = 0.00129t_{132} + 0.00126t_{133} + 0.00152vf$', r'$Cv_1$'),
    (r'$Cv_2 = 0.69671t_{132} + 0.69489t_{133} + 0.17807vf$', r'$Cv_2$'),
    ('Objective function', r'J'),
]
y_label = ['PV', 'PV', 'IDX']
y_limits = [
    (0.07, 0.09),
    (38, 40),
    (None, None)
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
