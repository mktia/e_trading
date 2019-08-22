import numpy as np

from coin import Coin


class BlockChain:
    """
    デジタルコインの発行
    """


    def __init__(self, __voltage_length):
        """
        インスタンスの初期化
        """
        self.__func = Coin()
        self.__voltage_length = __voltage_length


    def generate_coin(self, packet):
        """
        発行関数を用いたデジタルコインの発行
        """
        return self.__func.f(packet.get_payload(), self.__voltage_length)
