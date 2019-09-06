# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt

input_file = input('input file: ')

df = pd.read_csv(f'./{input_file}')

# 色指定
cmap = plt.get_cmap('tab10')

# グラフオブジェクト、軸作成
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

# データ描画
ax1.bar(df['time'], df['el0/1'], label='eletricity D/S')
ax2.plot(df['time'], df['t&g0/1'], color=cmap(1), label='coin')

# ラベル
ax1.set_xlabel('time')
ax1.set_ylabel('Wh')
ax2.set_ylabel('coin')

# 凡例
handler1, label1 = ax1.get_legend_handles_labels()
handler2, label2 = ax2.get_legend_handles_labels()
ax1.legend(handler1 + handler2, label1 + label2, loc='upper left')

# グラフ表示
plt.show()
