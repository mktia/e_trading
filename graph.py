# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt

input_file = input('input file: ')

df = pd.read_csv(f'./{input_file}')

# 色指定
cmap = plt.get_cmap('tab10')

print("""
描画内容を選択してください
1: 一つの末端ルータの電力需給量とデジタルコイン保有量の変動
2: ローカルネットワークに属する各末端ルータの電力需給量またはデジタルコイン保有量の変動
3: ローカルネットワークに属する電力需給量とデジタルコイン保有量の末端ルータ同士の比較
4: デジタルコイン保有量に発行量を含むときの比較
5: 取引なしの場合との電力損失の比較
""")

process_number = int(input('number: '))


if process_number == 1:

    nw_id = int(input('network index: '))
    nd_id = int(input('node index: '))
    trade_mint = int(input('1. trade, 2. trade+mint  nunber: '))

    # グラフオブジェクト、軸作成
    fig = plt.figure(figsize=(14, 8), tight_layout=True)
    ax1 = fig.add_subplot(111)
    # 第二軸
    ax2 = ax1.twinx()

    # データ描画
    ax1.fill_between(df['time'], df[f'el{nw_id}/{nd_id}'], label='eletricity')
    if trade_mint == 1:
        ax2.plot(df['time'], df[f'tr{nw_id}/{nd_id}'],
                 color=cmap(1), label='coin (trade)')
    elif trade_mint == 2:
        ax2.plot(df['time'], df[f't&g{nw_id}/{nd_id}'],
                 color=cmap(1), label='coin (trade+mint)')

    # ラベル
    ax1.set_xlabel('step', fontdict={'fontsize': 16})
    ax1.set_ylabel('Wh', fontdict={'fontsize': 16})
    ax2.set_ylabel('coin', fontdict={'fontsize': 16})
    
    # タイトル
    ax1.set_title('demand+loss / supply & coin (trade+mint)', fontdict={'fontsize': 18})

    # 凡例
    handler1, label1 = ax1.get_legend_handles_labels()
    handler2, label2 = ax2.get_legend_handles_labels()
    ax1.legend(handler1 + handler2, label1 + label2, loc='upper left')


elif process_number == 2:

    nw_id = int(input('network index: '))
    nodes_length = int(input('the number of nodes: '))
    print('電力需給量 el / デジタルコイン保有量 (trade) tr / デジタルコイン保有量 (trade+mint) t&g')
    upper = input('data label of upper graph: ')
    lower = input('data label of lower graph: ')

    fig = plt.figure(figsize=(14, 8), tight_layout=True)
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    for i in range(nodes_length):
        ax1.plot(df['time'], df[f'{upper}{nw_id}/{i + 1}'], label=f'node{i + 1}')
        ax2.plot(df['time'], df[f'{lower}{nw_id}/{i + 1}'], label=f'node{i + 1}')

    if upper == 'el':
        ax1.set_ylabel('Wh', fontdict={'fontsize': 16})
    elif upper == 'tr'or upper == 't&g':
        ax1.set_ylabel('coin', fontdict={'fontsize': 16})
    if lower == 'el':
        ax2.set_ylabel('Wh', fontdict={'fontsize': 16})
    elif lower == 'tr'or lower == 't&g':
        ax2.set_ylabel('coin', fontdict={'fontsize': 16})
    ax2.set_xlabel('step', fontdict={'fontsize': 16})

    if upper == 'el':
        ax1.set_title('demand+loss / supply', fontdict={'fontsize': 16})
    elif upper == 'tr'or upper == 't&g':
        ax1.set_title('amount of coin (trade)', fontdict={'fontsize': 16})
    if lower == 'el':
        ax2.set_title('demand+loss / supply', fontdict={'fontsize': 16})
    elif lower == 'tr':
        ax2.set_title('amount of coin (trade)', fontdict={'fontsize': 16})
    elif lower == 't&g':
        ax2.set_title('amount of coin (trade+mint)', fontdict={'fontsize': 16})

    ax1.legend()
    ax2.legend()


elif process_number == 3:

    nw_id = int(input('network index: '))
    nodes_length = int(input('the number of nodes: '))

    fig = plt.figure(figsize=(14, 8), tight_layout=True)
    axs_main = [fig.add_subplot(int(f'22{i + 1}'))
                for i in range(nodes_length)]
    axs_sub = [ax.twinx() for ax in axs_main]

    for i in range(nodes_length):
        axs_main[i].fill_between(df['time'], df[f'el{nw_id}/{i + 1}'], label='electricity')
        axs_sub[i].plot(df['time'], df[f't&g{nw_id}/{i + 1}'], color=cmap(1), label='coin (trade+mint)')

    axs_main[2].set_xlabel('step')
    axs_main[3].set_xlabel('step')
    axs_main[0].set_ylabel('Wh')
    axs_main[2].set_ylabel('Wh')
    axs_sub[1].set_ylabel('coin')
    axs_sub[3].set_ylabel('coin')

    for i, ax in enumerate(axs_main):
        ax.set_title(f'node {i + 1}')

    handlers_main=[]
    handlers_sub=[]
    labels_main=[]
    labels_sub=[]
    for ax in axs_main:
        handler, label = ax.get_legend_handles_labels()
        handlers_main.append(handler)
        labels_main.append(label)
    for ax in axs_sub:
        handler, label=ax.get_legend_handles_labels()
        handlers_sub.append(handler)
        labels_sub.append(label)
    for i, ax in enumerate(axs_main):
        ax.legend(handlers_main[i] + handlers_sub[i], labels_main[i] + labels_sub[i])


elif process_number==4:

    nw_id=int(input('network index: '))
    nd_id=int(input('node index: '))

    fig=plt.figure(figsize=(14,4), tight_layout=True)
    ax1_main=fig.add_subplot(121)
    ax2_main=fig.add_subplot(122)
    ax1_sub=ax1_main.twinx()
    ax2_sub=ax2_main.twinx()

    # 第二軸の範囲を共有
    # ax1_sub.get_shared_y_axes().join(ax1_sub, ax2_sub)

    ax1_main.fill_between(df['time'], df[f'el{nw_id}/{nd_id}'], label='eletricity')
    ax1_sub.plot(df['time'], df[f't&g{nw_id}/{nd_id}'], color=cmap(1), label='coin (trade+mint)')
    ax2_main.fill_between(df['time'], df[f'el{nw_id}/{nd_id}'], label='eletricity')
    ax2_sub.plot(df['time'], df[f'tr{nw_id}/{nd_id}'], color=cmap(1), label='coin (trade)')

    ax1_main.set_xlabel('step', fontdict={'fontsize': 14})
    ax2_main.set_xlabel('step', fontdict={'fontsize': 14})
    ax1_main.set_ylabel('Wh', fontdict={'fontsize': 14})
    ax2_sub.set_ylabel('coin', fontdict={'fontsize': 14})

    ax1_main.set_title('demand+loss / supply & trade+mint', fontdict={'fontsize': 14})
    ax2_main.set_title('demand+loss / supply & trade', fontdict={'fontsize': 14})

    handler1_main, label1_main=ax1_main.get_legend_handles_labels()
    handler1_sub, label1_sub=ax1_sub.get_legend_handles_labels()
    handler2_main, label2_main=ax2_main.get_legend_handles_labels()
    handler2_sub, label2_sub=ax2_sub.get_legend_handles_labels()
    ax1_main.legend(handler1_main + handler1_sub, label1_main + label1_sub, loc='upper left')
    ax2_main.legend(handler2_main + handler2_sub, label2_main + label2_sub, loc='upper left')


elif process_number==5:

    notrading_file_name=input('notrading file name:')
    df2=pd.read_csv(f'./{notrading_file_name}')

    fig=plt.figure(figsize=(14,4), tight_layout=True)
    ax1=fig.add_subplot(121)
    ax2=fig.add_subplot(122)
    # ax1_notrade=ax1_main.twinx()
    # ax2_notrade=ax2_main.twinx()
    
    ax1.plot(df['time'], df['ls_cml_nw0'], label='trade')
    ax1.plot(df2['time'], df2['ls_cml_nw0'], label='no trade')
    ax2.plot(df['time'], df['ls_cml_nw1'], label='trade')
    ax2.plot(df2['time'], df2['ls_cml_nw1'], label='no trade')

    ax1.set_xlabel('step')
    ax1.set_ylabel('loss [Wh]')
    ax2.set_xlabel('step')

    ax1.set_title('network 1')
    ax2.set_title('network 2')

    ax1.legend()
    ax2.legend()


# グラフ表示
plt.show()
