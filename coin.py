# -*- coding: utf-8 -*-

import numpy as np

class Coin():
    """
    デジタルコイン発行量と価格関数の設定
    """

    def __init__(self):
        # 供給された電力量の履歴
        self.y_history = [0]
        self.__history = 0

 
    def f(self, packet, lamb=10**4):
        """
        デジタルコインの発行

        Returns:
            generated_coin (numpy.float64): 生成されたコイン
        """
        # 係数ベクトル
        k = np.ones(packet.get_voltage_length()) * 0.5

        y = np.matmul(k, packet.get_payload())

        # 履歴の保存
        #self.y_history.append(y)
        self.__history += y

        # 総供給を求める
        y_total = np.sum(np.array(self.y_history))

        tmp = np.exp(-1 * y_total)
        generated_coin = lamb * tmp / (1 + tmp)**2

        return generated_coin


    def g(self, middle_node, nodes, voltage_index, lamb=10):
        """
        電力価格の決定

        Args:
            middle_node (node.Node): 中間ルータのオブジェクト
            nodes (List<node.Node>): 末端ルータのオブジェクトのリスト
            voltage_index (int): 取引する電力の電圧のインデックス
            lamb: 係数
        """
        surplus_in_network = 0
        for node in nodes:
            surplus_in_network += node.get_surplus_power()[voltage_index]
        surplus_in_network += middle_node.get_surplus_power()[voltage_index]

        # 中間ルータと接続されているすべての末端ルータの余剰電力量の合計より算出
        return lamb * np.exp(-1 * (surplus_in_network) / 100)
        # すべての末端ルータの余剰電力量の合計より算出
        # return lamb * np.exp(-1 * middle_node.get_network_surplus(nodes, voltage_index) / 100)
        # 中間ルータの余剰電力量より算出
        # return lamb * np.exp(-1 * middle_node.get_current_buffer(voltage_index) / 100)


    def c_(self):
        """
        for simulation5a.py
        電力パケットの到着ごとに定量を発行
        """
        return 10


    def c(self, packet):
        """
        電力パケットに含まれる電力量に応じて線形に発行
        """

        # 一回当たりの最大発行量
        max = 10

        return max * np.max(packet.get_payload()) / 20
