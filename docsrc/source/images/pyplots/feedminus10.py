import pandas as pd
import matplotlib.pyplot as plt

DIST = r"Disturbance: Decrease of 10% in the feed flowrate."

DATFOLDER = "dat_source/"

DATFILES = [
    "ic4_-10_at_the_feed_(26_kmol_h-1)_0.dat",
    "ic4_-10_at_the_feed_(26_kmol_h-1)_1.dat",
    "ic4_-10_at_the_feed_(26_kmol_h-1)_2.dat",
]

rows = len(DATFILES)
cols = 1

title_label = [
    ('Stage 32 Temperature - DIB', r'$c^{t32}_{1}$ (°C)'),
    ('Stage 14 Temperature - Purge', r'$c^{t14}_{2}$ (°C)'),
    ('IC5 Distillate composition', r'$ic^{d2}_{5}$ (°C)'),
]

y_limits = [
    (56, 58),
    (48.5, 51),
    (0.0, 0.012)
]

height = 10.0  # inches
aspect_ratio = 4 / 3
width = aspect_ratio * height

fig, axs = plt.subplots(rows, cols)
fig.set_size_inches(width, height)


for i, filename in enumerate(DATFILES):
    ax = axs[i]
    ymin, ymax = y_limits[i]
    title, ylabel = title_label[i]

    title = DIST + '\n' + title

    df = pd.read_csv(DATFOLDER + filename, sep='\t')

    time = df['Time']
    pv = df['PV']

    ax.plot(time, pv, color='blue')
    ax.grid(which='both')
    ax.set_title(title)
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel(ylabel)
    ax.set_ylim(ymin, ymax)

plt.tight_layout()
plt.show()
