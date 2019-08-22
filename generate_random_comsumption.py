from datetime import datetime
import numpy as np

execute_time = datetime.now().strftime('%Y%m%d%H%M%S')
PATH = './results'

# 電圧の種類
voltage_length = 5

# 乱数の範囲
min = -1
max = 1

# 末端ルータの総数
len_nodes = 8

# シミュレーションの試行回数
iterate = 20000

# 出力ファイル数
input_str = input('How many?: ')

# 数字以外が入力されたら１試行
count = int(input_str) if input_str.isdecimal() else 1

for i in range(count):
    random_vectors = [
        np.random.randint(min, max + 1, voltage_length) * 1.0 for i in range(iterate * len_nodes)
    ]

    with open(f'{PATH}/{execute_time}_random_{i}.csv', 'w') as f:
        for vector in random_vectors:
            for i in range(len(vector)):
                value = f'{vector[i]},' if i != len(
                    vector) - 1 else f'{vector[i]}\n'
                f.write(value)
