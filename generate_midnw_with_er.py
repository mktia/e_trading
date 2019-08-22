import numpy as np
from datetime import datetime

execute_time = datetime.now().strftime('%Y%m%d%H%M%S')

len_middle_node = 20

# 出力用
res = [[] for i in range(len_middle_node)]

# 閾値
p = 0.5

for node_id in range(len_middle_node):
    for i in range(len_middle_node):
        
        # 自分自身は除外
        if node_id == i:
            continue

        if np.random.random() > p:
            res[node_id].append((i, 0))

for i in res:
    print(i)
