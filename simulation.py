# -*- coding: utf-8 -*-

from datetime import datetime
import time as tm
from copy import deepcopy

import csv
import numpy as np
from tqdm import tqdm

from coin import Coin
from node import Node
from packet import Packet

# 実行日時の記録用
execute_time = datetime.now().strftime('%Y%m%d%H%M%S')

# 保存するディレクトリの指定
RESULT_DIR = './results'

# 電力パケットに含まれる電力量の上限
payload_amount = 20
# 取引を行う電力量の閾値
border = 0
# ローカルネットワークの数
world_size = 2
# 一つのローカルネットワークに属するルータ数 (中間ルータ含む)
network_size = 5
# 一つのローカルネットワークに属する末端ルータ数
network_edge = 4
# 電圧の種類
voltage_length = 5

# 全ノードの履歴
history = []
packets_history = []
payment_history = []
nodes_dict = {}

# 余剰電力量の情報
tmp = np.array([np.zeros(voltage_length) for i in range(network_edge)])
# network.edge.voltage
surplus_matrix = np.array([deepcopy(tmp) for i in range(world_size)])

tmp = tuple([] for i in range(voltage_length))
# network.voltage.location
queue = tuple(deepcopy(tmp) for i in range(world_size))
# 中間ルータにおける電力分布を保存
el_queue = tuple(np.zeros(network_edge) for i in range(world_size))

# 中間ルータ同士の接続状態
middle_network = [
    [(1, 0)],
    [(0, 0)]
]

blockchain = Coin()

random_consumption = []
input_file = input('consumption file: ')
with open(f'./{input_file}', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        values = [float(i) for i in row]
        random_consumption.append(np.array(values))


def get_price(amount, trading_voltage, network_index):
    """
    価格決定
    """
    middle = nodes_dict[str((network_index, 0))]
    power_in_network = np.sum(surplus_matrix[network_index], axis=0)[trading_voltage] + middle.get_surplus()[trading_voltage]
    if amount == None:
        # NOTE: パケット当たりの価格
        return 10 * np.exp(-1 * power_in_network / 1000)
    else:
        return 10 * np.exp(-1 * power_in_network / 1000) * (amount / 20)


def get_price_linear(amount):
    """
    価格決定
    余剰電力量に依存せず、パケットに含まれる電力量で線形に変動
    """
    return 10 * amount / 20


def get_price_uniform():
    """
    価格決定
    パケットに含まれる電力量に依存せず、定額
    """
    return 10


def make_demand_packet_random(me, selected):
    """
    中間ルータが需要を送信するパケット
    """
    surplus = nodes_dict[str(me)].get_surplus()
    return Packet(tuple(me), tuple(selected), np.copy(surplus), np.zeros(len(surplus)))


def make_supply_packet(packet):
    """
    需要に対する供給を行うパケット
    """
    # ペイロードの初期化
    payload_placeholder = np.zeros(packet.get_voltage_length())
    # パケットの余剰電力情報
    surplus = np.copy(packet.get_surplus())
    # 送信、受信者は demand packet の逆
    sender = nodes_dict[str(packet.get_to())]
    receiver = nodes_dict[str(packet.get_from())]

    while True:
        # 余剰電力量最小の電圧を取得
        trading_voltage = np.argmin(surplus)
        # 最小電力量が 0 より大きい場合
        if surplus[trading_voltage] > 0:
            break
        else:
            # 送信分の電力がある場合
            if sender.get_surplus()[trading_voltage] >= 0.1:
                # 数値のずれを吸収するため
                record = queue[sender.get_network()][trading_voltage][0]
                # 最小電力量の電圧の電力を送信
                payload_placeholder[trading_voltage] = record['amount']
                return Packet(tuple(sender.get_location()), tuple(receiver.get_location()), np.copy(sender.get_surplus()), np.copy(payload_placeholder))
            else:
                surplus[trading_voltage] = 100000

    return None


def make_packet_to_middle(sender):
    """
    Args:
        sender: 末端ルータ
    """
    # ペイロードの初期化
    payload_placeholder = np.zeros(sender.get_voltage_length())
    # 最大電力量の電圧を取得
    voltage_index = np.argmax(sender.get_surplus())
    # 最大電力量が payload_amount より大きい場合
    if sender.get_surplus()[voltage_index] >= payload_amount:
        # 最大電力量の電圧の電力を送信
        payload_placeholder[voltage_index] = payload_amount
    # 最大電力量が border より大きい場合
    elif sender.get_surplus()[voltage_index] > border:
        payload_placeholder[voltage_index] = sender.get_surplus()[voltage_index]
    # 最大電力量が 0 以下であれば余剰電力量情報のみ伝達
    return Packet(tuple(sender.get_location()), tuple((sender.get_network(), 0)), np.copy(sender.get_surplus()), np.copy(payload_placeholder))


def make_packet_to_prior_node(sender):
    """
    Args:
        sender: 中間ルータ
    """
    if np.max(sender.get_surplus()) <= 0:
        # 中間ルータの電力不足
        return None

    payload_placeholder = np.zeros(sender.get_voltage_length())

    matrix = np.copy(surplus_matrix[sender.get_network()])

    while True:
        # about voltage
        tmp_power = np.min(matrix, axis=1)
        voltage_indices = np.argmin(matrix, axis=1)
        power = np.min(tmp_power)
        node_index = np.argmin(tmp_power)

        trading_voltage = voltage_indices[node_index]

        if power >= border:
            # 送電先の電力が十分である場合
            return None
        elif sender.get_surplus()[trading_voltage] >= 0.1:
            # 数値の誤差を吸収するため
            """
            print(sender.get_location())
            print(sender.get_surplus())
            print(queue[sender.get_network()])
            print(f'vol: {trading_voltage}')
            """
            if len(queue[sender.get_network()][trading_voltage]) != 0:
                # 需要情報に対してマッチングする電力が中間ルータにある場合
                record = queue[sender.get_network()][trading_voltage][0]
                payload_placeholder[trading_voltage] = record['amount']
                return Packet(tuple(sender.get_location()), tuple((sender.get_network(), node_index + 1)), np.copy(sender.get_surplus()), np.copy(payload_placeholder))

        matrix[node_index][trading_voltage] = border


def send_among_middle(packet):
    """
    中間ルータの数に応じて変更
    """
    sender = nodes_dict[str(packet.get_from())]
    receiver = nodes_dict[str(packet.get_to())]

    sender.discharge(packet)
    receiver.charge(packet)

    trading_voltage = np.argmax(packet.get_payload())

    # キューの内容を移動
    record = queue[sender.get_network()][trading_voltage].pop(0)
    queue[receiver.get_network()][trading_voltage].append(record)


def send_to_middle(packet, generated_coin):
    """
    末端ルータから中間ルータへ
    """
    sender = nodes_dict[str(packet.get_from())]
    receiver = nodes_dict[str(packet.get_to())]

    sender.discharge(packet)
    receiver.charge(packet)

    sender.receive_generated(generated_coin)

    # 取引する電力のインデックス
    trading_voltage = np.argmax(packet.get_payload())

    # 優先送電用に記録
    network_index, node_index = sender.get_location()
    # 情報通信用パケット以外をキューに記録
    if np.max(packet.get_payload()) != 0:
        # 電力分布記録の更新
        el_queue[network_index][node_index - 1] += packet.get_payload()[trading_voltage]
        queue[network_index][trading_voltage].append({'location': sender.get_location(), 'amount': packet.get_payload()[trading_voltage]})
        surplus_matrix[network_index][node_index - 1] = sender.get_surplus()


def send_to_node(packet):
    """
    中間ルータから末端ルータへ
    """
    sender = nodes_dict[str(packet.get_from())]
    receiver = nodes_dict[str(packet.get_to())]

    sender.discharge(packet)
    receiver.charge(packet)

    # sender_network_index, sender_node_index = sender.get_location()
    receiver_network_index, receiver_node_index = receiver.get_location()

    # 余剰電力の情報を更新
    surplus_matrix[receiver_network_index][receiver_node_index - 1] += packet.get_payload()

    # 取引する電力のインデックス
    trading_voltage = np.argmax(packet.get_payload())
    # 取引する電力量
    trading_amount = np.max(packet.get_payload())

    # 価格決定
    #price = get_price(trading_voltage, sender.get_network())
    # 余剰電力量情報＋周辺の電力から価格決定
    # price = get_price(trading_amount, trading_voltage, sender.get_network())
    # パケットで定額
    price = get_price_linear(trading_amount)

    # キューから取得
    record = queue[network_index][trading_voltage].pop(0)
    # 電力分布記録の更新
    el_queue[receiver_network_index][receiver_node_index - 1] -= trading_amount
    
    # 需要家の支払い
    receiver.pay(price)
    # 供給者の受け取り
    nodes_dict[str(record['location'])].receive(price)

    return price


def record_packet_history(time, inout, packet):
    packets_history.append(
        [
            [time],
            [inout],
            [f'{packet.get_from()[0]}|{packet.get_from()[1]}'],
            [f'{packet.get_to()[0]}|{packet.get_to()[1]}'],
            np.copy(packet.get_surplus()),
            np.copy(packet.get_payload())
        ]
    )


if __name__ == '__main__':

    trial_count = 1
    # file_base_name = input('random file: ')
    # random_files = [f'{file_base_name}_{i}' for i in range(trial_count)]
    output_files = []
    output_timers = []

    for trial in tqdm(range(trial_count)):

        execute_time = datetime.now().strftime('%Y%m%d%H%M%S')
        # シミュレーション回数
        simulation_length = 10000
        # 電力使用の頻度
        use_span = 10
        # 電力使用量変動の間隔
        use_step = 1
        # 電力使用量の幅
        use_width = 1
        # 中間ルータ同士の取引の頻度
        middle_span = 1
        buffer_edge = np.ones(voltage_length) * 3000
        buffer_middle = np.ones(voltage_length) * 5000
        # デジタルコインの初期保有量
        initial_coin = 100

        # ルータの初期化
        nodes = []
        nodes.append(Node((0, 0), '(0, 0)', buffer_middle, np.zeros(voltage_length), 0, 0, connected=middle_network[0], type='middle'))
        nodes.append(Node((0, 1), '(0, 1)', buffer_edge, np.array(random_consumption.pop(0)), initial_coin, 0))
        nodes.append(Node((0, 2), '(0, 2)', buffer_edge, np.array(random_consumption.pop(0)), initial_coin, 0))
        nodes.append(Node((0, 3), '(0, 3)', buffer_edge, np.array(random_consumption.pop(0)), initial_coin, 0))
        nodes.append(Node((0, 4), '(0, 4)', buffer_edge, np.array(random_consumption.pop(0)), initial_coin, 0))
        nodes.append(Node((1, 0), '(1, 0)', buffer_middle, np.zeros(voltage_length), 0, 0, connected=middle_network[1], type='middle'))
        nodes.append(Node((1, 1), '(1, 1)', buffer_edge, np.array(random_consumption.pop(0)), initial_coin, 0))
        nodes.append(Node((1, 2), '(1, 2)', buffer_edge, np.array(random_consumption.pop(0)), initial_coin, 0))
        nodes.append(Node((1, 3), '(1, 3)', buffer_edge, np.array(random_consumption.pop(0)), initial_coin, 0))
        nodes.append(Node((1, 4), '(1, 4)', buffer_edge, np.array(random_consumption.pop(0)), initial_coin, 0))

        # ノード対応辞書
        nodes_dict = {node.get_name():node for node in nodes}

        # 初期値の表示
        # for node in nodes:
        #     print(f'{node.get_name()} {node.get_surplus()}')

        # インデックス行
        tmp = [[0]]
        for node in nodes:
            # ノードラベル
            tmp.append(['nd' + str(node.get_name()).replace(', ', '/').replace('(', '').replace(')', '') for i in range(nodes[0].get_voltage_length())])
        # コインラベル
        tmp.append(['c' + str(node.get_name()).replace(', ', '/').replace('(', '').replace(')', '') for node in nodes])
        # generated
        tmp.append(['gen' + str(node.get_name()).replace(', ', '/').replace('(', '').replace(')', '') for node in nodes])
        # price (each NW)
        tmp.append(np.arange(nodes[0].get_voltage_length()))
        tmp.append(np.arange(nodes[0].get_voltage_length()))
        # 電力分布のラベル
        for network in range(world_size):
            tmp.append([f'el{network}/{node_id + 1}' for node_id in range(network_edge)])
        history.append(tmp)


        # 初期値の記録
        tmp = [[0]]
        tmp += [deepcopy(node.get_surplus()) for node in nodes]
        # コインの初期値
        tmp.append([node.get_coin() for node in nodes])
        # generated
        tmp.append([node.get_generated_coin() for node in nodes])
        # price
        tmp += [np.zeros(nodes[0].get_voltage_length()) for i in range(world_size)]
        # 電力分布の初期値
        for network_el_queue in el_queue:
            tmp.append(np.copy(network_el_queue))
        history.append(tmp)

        # 各ネットワークのルータ数
        network_list = np.zeros(world_size)
        for i in range(world_size):
            for node in nodes:
                if i == node.get_network():
                    network_list[i] += 1
                elif i < node.get_network():
                    break

        start_time = tm.perf_counter_ns()
        # 実行時間測定
        # for i in tqdm(range(simulation_length)):
        for i in range(simulation_length):
            time = i + 1
            efficiency = 0.95

            if time % use_span == 0:
                for node in nodes:
                    # 自然放電
                    node.leak(efficiency)
                    if not node.is_middle():
                        node.consumption(random_consumption.pop(0))
                # 自然放電を電力分布の記録に反映
                for network in el_queue:
                    network *= efficiency
                # ロスを queue に反映
                for network in queue:
                    for voltage in network:
                        for record in voltage:
                            record['amount'] *= efficiency

            for network_index in range(world_size):
                # 末端ルータのランダムな選択
                sender = nodes_dict[str((network_index, np.random.randint(1, network_list[network_index])))]
                # パケットの生成
                packet = make_packet_to_middle(sender)
                # パケットを記録
                record_packet_history(time, 'IN', packet)
                # デジタルコインの発行
                #generated_coin = blockchain.f(packet)
                generated_coin = blockchain.c_linear(packet)
                # 末端ルータから中間ルータへの送電
                send_to_middle(packet, generated_coin)

                # 中間ルータの選択
                sender = nodes_dict[str((network_index, 0))]
                # パケットの生成
                packet = make_packet_to_prior_node(sender)
                #packet = make_packet_to_the_rich(sender)
                # 中間ルータから末端ルータへの送電
                if packet != None:
                    payment = send_to_node(packet)
                    # payment_history.append([time] + payment)
                    record_packet_history(time, 'OUT', packet)

            if time % middle_span == 0:
                for node in nodes:
                    if node.is_middle():
                        # 中間ルータ層での取引
                        packet = make_demand_packet_random(node.get_location(), node.select_middle())
                        packet = make_supply_packet(packet)
                        if packet != None:
                            record_packet_history(time, 'MID', packet)
                            send_among_middle(packet)

            tmp = [[time]]
            tmp += [deepcopy(node.get_surplus()).tolist() for node in nodes]
            # coin
            tmp.append([node.get_coin() for node in nodes])
            # generated
            tmp.append([node.get_generated_coin() for node in nodes])
            # price
            for network_index in range(world_size):
                middle = nodes_dict[str((network_index, 0))]
                # tmp.append([get_price(None, v, network_index) for v in range(middle.get_voltage_length())])
                tmp.append([get_price_uniform() for v in range(middle.get_voltage_length())])
            history.append(tmp)

            # 電力分布
            for network_el_queue in el_queue:
                tmp.append(np.copy(network_el_queue))


        end_time = tm.perf_counter_ns()

        # print(f'nodes history: {execute_time}_nodes')
        with open(f'{RESULT_DIR}/{execute_time}_nodes.csv', 'w') as f:
            # for h in tqdm(history):
            for h in history:
                for vector in h:
                    for v in vector:
                        f.write(f'{str(v)},')
                f.write('\n')
        output_files.append(f'{execute_time}_nodes.csv')

        print('packets history')
        with open(f'{RESULT_DIR}/{execute_time}_packets.csv', 'w') as f:
            f.write('time,inout,from,to,s_v1,s_v2,s_v3,s_v4,s_v5,p_v1,p_v2,p_v3,p_v4,p_v5\n')
            for h in packets_history:
                for vector in h:
                    for item in vector:
                        f.write(f'{item},')
                f.write('\n')

        # print('payments history')
        # with open(f'{HERE}/{execute_time}_payments.csv', 'w') as f:
        #     for h in tqdm(payment_history):
        #         for item in h:
        #             f.write(f'{item},')
        #         f.write('\n')

        # with open(f'{HERE}/{execute_time}_nodeappend.txt', 'w') as f:
        #     for node in nodes:
        #         if node.is_middle():
        #             f.write(f'nodes.append(Node({node.get_location()}, \'{node.get_location()}\', buffer_middle, np.array({node.get_surplus()}), 0, 0, connected=generated_network.pop(0), type=\'middle\'))\n')
        #         else:
        #             f.write(f'nodes.append(Node({node.get_location()}, \'{node.get_location()}\', buffer_edge, np.zeros(voltage_length), {node.get_coin()}, {node.get_generated_coin()}))\n')

        output_timers.append(f'{end_time - start_time}')

    with open(f'./{RESULT_DIR}/{execute_time}_results.txt', 'a') as f:
        f.write(f'{output_files.pop(0)}\n')
    with open(f'./{RESULT_DIR}/{execute_time}_timer.txt', 'a') as f:
        f.write(f'{output_timers.pop(0)}\n')
