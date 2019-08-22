# -*- coding: utf-8 -*-

import numpy as np

class Node():
    """
    ノード関連の設定
    """

    def __init__(self, __location, __name, __buffer_size, __surplus, __coin, __generated, connected=[], type='edge'):
        """
        Args:
            __location (tuple): __location[0]: index of node, __location[1]: index of network
            __name (str): ノードの名前
            __buffer_size (numpy.ndarray): 蓄電池の容量
            __surplus (numpy.ndarray): 余剰電力量
            __coin (float): デジタルコイン保有量
            __generated (float): ノードの電力供給で生成されたデジタルコインの量
            connected (list): (中間ルータの場合) 他の中間ルータの接続状況
            type (str): 末端ルータと中間ルータの区別 (初期値は末端ルータ)
        """
        self.__LOCATION = __location
        self.__NAME = __name
        self.__TYPE = type
        self.__BUFFER_SIZE = __buffer_size
        self.__surplus = np.array(__surplus)
        self.__coin = __coin
        self.__generated_coin = __generated
        # 電圧の種類の総数
        self.__voltage_length = len(__buffer_size)
        self.__connection = connected


    def get_location(self):
        """
        ローカルネットワークと中間ルータにおけるインデックスを取得
        """
        return self.__LOCATION


    def get_name(self):
        """
        
        """
        return self.__NAME


    def get_network(self):
        """

        """
        return self.__LOCATION[0]


    def get_surplus(self):
        """
        余剰電力量を取得
        """
        return self.__surplus


    def get_voltage_length(self):
        """
        ノードで扱う電力の電圧の種類の総数を取得
        """
        return self.__voltage_length


    def get_coin(self):
        """
        デジタルコインの保有量を取得
        """
        return self.__coin


    def get_generated_coin(self):
        """
        デジタルコインの生成量を取得
        """
        return self.__generated_coin


    def is_middle(self):
        """
        中間ルータか否か
        """
        if self.__TYPE == 'middle':
            return True
        else:
            return False


    def charge(self, packet):
        """
        電力を受ける

        Args:
            packet (packet.Packet)
        """
        self.__surplus += packet.get_payload()


    def discharge(self, packet):
        """
        電力を送る

        Args:
            packet (numpy.ndarray)
        """
        self.__surplus -= packet.get_payload()


    def pay(self, coin):
        """
        デジタルコインの支払い

        Args:
            coin (float): 支払うコインの量
        """
        self.__coin -= coin


    def receive(self, coin):
        """
        デジタルコインを受け取る
        """
        self.__coin += coin


    def receive_generated(self, coin):
        """
        生成されたデジタルコインを加算
        """
        self.__generated_coin += coin


    def use_power(self, width):
        """
        電力使用を再現
        """
        self.__surplus += np.random.randint(-1 * width, 1 + width, self.__voltage_length) * 1.0


    def leak(self, efficiency=0.95):
        """
        電力のリークを再現
        """
        for i in range(len(self.__surplus)):
            if self.__surplus[i] > 0:
                self.__surplus[i] *= efficiency


    def consumption(self, random_vector):
        """
        与えられたベクトルに従って電力使用を再現
        """
        self.__surplus += random_vector


    def select_middle(self):
        """
        中間ルータネットワークにおいて取引する相手となる中間ルータを選択する
        """
        return self.__connection[np.random.randint(len(self.__connection))]
