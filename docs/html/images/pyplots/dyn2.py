import matplotlib.pyplot as plt
import pandas as pd

import pathlib

# PARENTDIR = pathlib.Path(__file__).resolve().parent

# DATFILE = PARENTDIR / "ic4_+10_at_the_feed_(26_kmol_h-1)_0.dat"
DATFILE = "ic4_+10_at_the_feed_(26_kmol_h-1)_0.dat"

df = pd.read_csv(DATFILE, sep='\t')

time = df['Time']
pv = df['PV']

print(pv)
plt.plot(time, pv, color='blue')
plt.grid(which='both')
plt.title('Stage 32 Temperature. - DIB')
plt.xlabel('Time (hours)')
plt.ylabel(r'$c1_{t32}$ (°C)')

plt.show()
