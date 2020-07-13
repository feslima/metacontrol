import pandas as pd
import matplotlib.pyplot as plt


DIST = r"Disturbance: Increase of 2.5% in feed composition."
DATFOLDER = "dat_source/"
DATFILES = [
    "cpu_+2,5_CO2_0.dat",
    "cpu_+2,5_CO2_1.dat",
    "cpu_+2,5_CO2_2.dat",
    "cpu_+2,5_CO2_3.dat",
    "cpu_+2,5_CO2_4.dat",
    "cpu_+2,5_CO2_4.dat",
]

rows = 2
cols = 3

title_label = [
    ('MCC Discharge Temperature', r'$mcct$ (°C)'),
    ('F1 Temperature', r'$f1$ (°C)'),
    ('F2 Temperature', r'$f2$ (°C)'),
    ('S8 Temperature', r'$s8t$ (°C)'),
    (r'$CO_2$ Recovery', r'$co2rr$'),
    (r'$CO_2$ Purity', r'$xco2out$'),
]
y_label = ['PV', 'PV', 'PV', 'PV', 'RR_CO2', r'STREAMS("S-21").Zn("CO2")']
y_limits = [
    (24.75, 25.05),
    (-31, -29),
    (-56, -54),
    (-56.4, -54.4),
    (0.956, 0.978),
    (0.964, 0.974),
]
height = 10.0  # inches
aspect_ratio = 4 / 3
width = aspect_ratio * height


def plot_graph(DIST: str, DATFOLDER: str, DATFILES: list,
               rows: int, cols: int, y_labels: list, y_limits: list,
               title_label: list, width: float, height: float):

    fig, axs = plt.subplots(rows, cols)
    fig.patch.set_visible(False)
    fig.set_size_inches(width, height)

    for i, filename in enumerate(DATFILES):
        ax = axs.item(i)
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
