import csv
from datetime import datetime
from copy import deepcopy
import numpy as np
from tqdm import tqdm

# 電力損失
efficiency = 0.95
# 中間ルータの数
world_size = 2
# LNに属する末端ルータの数
network_edge = 4
# 電圧の種類
voltage_length = 5
# シミュレーション回数
simulation_length = 10000

# 実行日時の記録用
execute_time = datetime.now().strftime('%Y%m%d%H%M%S')

# 保存するディレクトリの指定
RESULT_DIR = './results'

random_consumption = []
input_file = input('consumption file: ')
with open(f'./{input_file}', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        values = [float(i) for i in row]
        random_consumption.append(np.array(values))


def pickup_surplus(electricity):
    """
    電力損失が発生する電圧の電力のみを抽出

    Args
        electricity (numpy.ndarray): ノードの余剰電力量
    """
    loss = np.zeros(electricity.size)
    for id, item in enumerate(electricity):
        if item > 0:
            loss[id] = item

    return loss


el_amount = [[np.array(random_consumption.pop(0))
              for i in range(network_edge)] for j in range(world_size)]
ls_amount = [[0 for nd in range(network_edge)] for nw in range(world_size)]
ls_cumul_amount = [[0 for nd in range(network_edge)]
                   for nw in range(world_size)]

# 変数名の省略
nws = world_size
nds = network_edge
# time
label = ['time']
# surplus
label += [f'nd{nw}/{nd + 1}' for nw in range(nws)
          for nd in range(nds) for i in range(5)]
# loss
label += [f'ls{nw}/{nd + 1}' for nw in range(nws) for nd in range(nds)]
# cumulative loss
label += [f'ls_cml{nw}/{nd + 1}' for nw in range(nws) for nd in range(nds)]
# cumulative loss in each network
label += [f'ls_cml_nw{nw}' for nw in range(nws)]

# ラベル
output = [label]

# 初期値
# time
res = [0]
# surplus
res += [amount for el_nw in el_amount for el_nd in el_nw for amount in el_nd]
# loss
res += [amount for nw in ls_amount for amount in nw]
# cumulative loss
res += [amount for nw in ls_cumul_amount for amount in nw]
# cumulative loss in each network
res += [np.sum(nw) for nw in ls_cumul_amount]

output.append(res)


for i in range(simulation_length):
    time = i + 1

    if time % 10 == 0:
        for nw, el_network in enumerate(el_amount):
            for nd, el_node in enumerate(el_network):
                # 損失した電力量
                loss_in_node = pickup_surplus(el_node) * (1 - efficiency)
                # 瞬間的な電力損失の記録
                ls_amount[nw][nd] = np.sum(loss_in_node)
                # 累積の電力損失の記録
                ls_cumul_amount[nw][nd] += np.sum(loss_in_node)
                # 自然放電
                el_node -= loss_in_node
                # 電力の消費生産
                el_node += random_consumption.pop(0)

    res = [time]
    # 取引なしの余剰電力量
    res += [amount for el_nw in el_amount for el_nd in el_nw for amount in el_nd]
    # 瞬間的電力損失量
    res += [amount for nw in ls_amount for amount in nw]
    # 累積電力損失量
    res += [amount for nw in ls_cumul_amount for amount in nw]
    # ネットワーク別累積電力損失量
    res += [np.sum(nw) for nw in ls_cumul_amount]

    output.append(res)


print('Saving...')
with open(f'./{RESULT_DIR}/{execute_time}_notrading.csv', 'w', newline='') as f:
    for row in tqdm(output):
        writer = csv.writer(f)
        writer.writerow(row)
