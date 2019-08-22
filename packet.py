import numpy as np


class Packet:

    def __init__(self, __from, __to, __surplus, __payload):
        """
        Args:
            __from (int): 送信元ルータのインデックス
            __to (int): 送信先ルータのインデックス
            __surplus: 余剰電力量情報
            __payload (numpy.ndarray): 電圧別の電力の実体を表す
        """
        self.__header = {'from': __from, 'to': __to, 'surplus': __surplus}
        self.__payload = __payload
        self.__footer = None


    def get_from(self):
        """
        送信元の取得
        """
        return self.__header['from']


    def get_to(self):
        """
        宛先の取得
        """
        return self.__header['to']


    def get_header(self):
        """
        ヘッダーの取得
        """
        return self.__header


    def get_payload(self):
        """
        ペイロードの取得
        """
        return self.__payload


    def get_surplus(self):
        """
        余剰電力量情報の取得
        """
        return self.__header['surplus']


    def get_voltage_length(self):
        """
        電圧の種類の数を取得
        """
        return len(self.__payload)
