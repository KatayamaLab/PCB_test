import pathlib
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from natsort import natsorted
from scipy.signal import windows
import argparse
import csv
import pprint

f = 1000
t = 1 / f

fig, ax = plt.subplots()


# data_path2 = pathlib.Path("./result")
real2, imag2 = [], []
idx2_ch1, idx2_ch2 = {}, {}
frequency, ch1_spectre2, ch2_spectre2 = {}, {}, {}
impedance_list2 = []
# data_path2.glob(f"measurement_data2")
ch1_buff2, ch2_buff2 = [], []

# 5周期分解析を行う
Ts = 7.8125*10**-6
meas_data2 = pd.read_csv('a/measurement_data6.csv', skiprows=1)
# meas_data2 = pd.read_csv(p, skiprows=25)
# Fourier transform
# print(meas_data2.shape)
# print(meas_data2.columns)

freq = np.fft.rfftfreq(len(meas_data2), d=Ts)[1:]
F2_ch1 = np.fft.rfft(meas_data2.iloc[:, 1].to_numpy())[1:]
F2_ch2 = np.fft.rfft(meas_data2.iloc[:, 2].to_numpy())[1:]
# Extract near target frequency
freq_lower2 = f * 0.85
freq_upper2 = f * 1.15
# Get max spectre
F2_ch1_ = F2_ch1.copy()
F2_ch2_ = F2_ch2.copy()
F2_ch1_[~((freq_lower2 < freq) & (freq < freq_upper2))] = 0
F2_ch2_[~((freq_lower2 < freq) & (freq < freq_upper2))] = 0
max_spectre_idx_v2 = np.argmax(np.abs(F2_ch1_))
max_spectre_idx_i2 = np.argmax(np.abs(F2_ch2_))
idx2_ch1[f] = max_spectre_idx_v2
idx2_ch2[f] = max_spectre_idx_i2
N = len(meas_data2)
ch1_buff2.append(np.abs(F2_ch1) / (N / 2))
ch2_buff2.append(np.abs(F2_ch2) / (N / 2))
# # Calc impedance
impedance_list2.append(
    F2_ch1[max_spectre_idx_v2] / F2_ch2[max_spectre_idx_i2])
frequency[f] = freq
ch1_spectre2[f] = np.average(ch1_buff2, axis=0)
ch2_spectre2[f] = np.average(ch2_buff2, axis=0)


impedance2 = np.average(impedance_list2, axis=0)
z_angle2 = np.degrees(np.arctan2(impedance2.imag, impedance2.real))

# real2.append(impedance2.real)
# imag2.append(-impedance2.imag)
# real3.append(impedance3.real)
# imag3.append(-impedance3.imag)

# ax.scatter(real, imag, s=10, label="analyzer")
# ax.scatter(real2, imag2, s=10, label="single")


# ax.set(aspect='equal')
# ylim=(0.0028,0.0038)
# plt.scatter(real, imag,label="analyzer")
# plt.scatter(real2, imag2,label="single")
# # # plt.scatter(real3, imag3,label="analyzer")
# plt.legend()
# plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.5),
#            fontsize='small', borderaxespad=0, handletextpad=-0.3, borderpad=0.3)
# plt.show()
# print(z_angle)
# print(z_angle2)
# # print(z_angle3)

fig = plt.figure(figsize=(20, 10))

ax_ch1 = fig.add_subplot(121)

# ax_ch1.set_yscale("log")

# print(frequency[f])


for k, v in ch1_spectre2.items():

    ax_ch1.plot([k, k], [0, 0.05], c="red", linestyle="dashed")

    ax_ch1.bar(frequency[k], v, width=20)
    # ax_ch1.plot(frequency[k], v, label=f"{k} Hz", c=cm.jet((k - 10) / (1000 - 10)),)

ax_ch2 = fig.add_subplot(122)

# ax_ch2.set_yscale("log")

for k, v in ch2_spectre2.items():
    ax_ch2.plot([k, k], [0, 0.3], c="red", linestyle="dashed")
    ax_ch2.bar(frequency[k], v, width=20)
    # ax_ch2.scatter(frequency[k],v)
    # ax_ch2.plot(frequency[k], v, label=f"{k} Hz", c=cm.jet((k - 10) / (1000 - 10)))


# ax_ch1.set_ylim((0, 0.02))
# ax_ch2.set_ylim((0, 1))
# ax_ch1.legend()
# # ax_ch2.legend()
ax_ch1.set_xlim((10, 2000))
ax_ch2.set_xlim((10, 2000))
# ax_ch1.set_ylim(0, 200)
# ax_ch2.set_ylim(0, 200)
ax_ch1.set_xlabel("frequency [Hz]", fontsize="20")
ax_ch2.set_xlabel("frequency [Hz]", fontsize="20")
# y 軸のラベルを設定する。
ax_ch1.set_ylabel("votage [V]", fontsize="20")
ax_ch2.set_ylabel("current [A]", fontsize="20")
ax_ch1.tick_params(labelsize=20, axis='x', labelrotation=45)
ax_ch2.tick_params(labelsize=20, axis='x', labelrotation=45)
ax_ch1.tick_params(labelsize=22, axis='y', labelrotation=0)
ax_ch2.tick_params(labelsize=22, axis='y', labelrotation=0)
fig.savefig(f"{f}Hz_spector_3.png", dpi=400)
exit()
