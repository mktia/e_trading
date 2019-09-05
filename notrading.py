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

label = ['time'] + [f'nd{network_index}/{node_index + 1}'
                    for network_index in range(world_size) for node_index in range(network_edge) for i in range(5)]

el_amount = [[np.array(random_consumption.pop(0))
              for i in range(network_edge)] for j in range(world_size)]

output = [label]
output.append(
    ['0'] + [el_item for el_network in el_amount for el_node in el_network for el_item in el_node])

for i in range(simulation_length):
    time = i + 1

    if time % 10 == 0:

        for el_network in el_amount:
            for el_node in el_network:
                # 自然放電
                el_node *= efficiency
                # 電力の消費生産
                el_node += random_consumption.pop(0)

    output.append(
        [time] + deepcopy([el_item for el_network in el_amount for el_node in el_network for el_item in el_node]))


print('Saving...')
with open(f'./{RESULT_DIR}/{execute_time}_notrading.csv', 'w', newline='') as f:
    for row in tqdm(output):
        writer = csv.writer(f)
        writer.writerow(row)
