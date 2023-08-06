import requests
import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
from tqdm.auto import tqdm
from pylab import rcParams
from datetime import datetime
from src.conf import customers, costs, discounts, prices_path, EU_LOGISTIC_COST_EUR, CN_LOGISTIC_COST_USD

def calculate_prices():
    print('hello world')
    seaborn.set()

    # Подгружаем котировки курсы
    print("Подгружаем котировки и курсы")
    all_dfs=[]
    for y in tqdm(['2019', '2020', '2021']):
        for m in ['01', '02']:
            url = f"https://www.lgm.gov.my/webv2api/api/rubberprice/month={m}&year={y}"
            res = requests.get(url)
            rj = res.json()
            temp_df = pd.json_normalize(rj)
            all_dfs.append(temp_df)
    df = pd.concat(all_dfs)
    df = df.set_index('date')
    df = df.reset_index()
    df.date = pd.to_datetime(df['date'], format='%Y-%m-%d')
    

    # Рассчитываем цены
    print("Рассчитываем цены")
    df['PRICE_USD'] = pd.to_numeric(df['us'], downcast='float') * 1000 / 100
    df['PRICE_USD_EU'] = df['PRICE_USD'] + EU_LOGISTIC_COST_EUR * 1.02
    df['PRICE_USD_CN'] = df['PRICE_USD'] + CN_LOGISTIC_COST_USD
    df['PRICE_USD_MA'] = df.PRICE_USD_EU.rolling(window=3).mean()
    df = df.groupby(['date']).mean()
    df = df.loc['2019-06-30':'2022-06-30'].copy()


    # Создаем отдельный файл для каждого из клиентов


    rcParams['figure.figsize'] = 15,7

    print("Готовим отдельный файл для клиентов")
    for client, v in customers.items():

        # Создаем директорию и путь к файлу
        client_price_path = os.path.join(prices_path, f"{client.lower()}")
        if not os.path.exists(client_price_path):
            os.makedirs(client_price_path)

        calculation_date = datetime.today().date().strftime(format="%d%m%Y")
        client_price_file_path = os.path.join(client_price_path, f'{client}_mwp_price_{calculation_date}.xlsx')

        location = v.get('location')
        disc = 0.0
        if v.get('location') == "EU":
            fl = 0
            for k_lim, discount_share in discounts.items():
                if v.get('volumes') > k_lim:
                    continue
                else:
                    disc = discount_share
                    fl = 1
                    break
            if fl == 0:
                disc = discounts.get(max(discounts.keys()))

            if v.get('comment') == 'monthly':
                client_price = df['PRICE_USD_EU'].mul((1 - disc)).add(costs.get('EU_LOGISTIC_COST_EUR')).round(2)
            elif v.get('comment') == 'moving_average':
                client_price = df['PRICE_USD_MA'].mul((1 - disc)).add(costs.get('EU_LOGISTIC_COST_EUR')).round(2)

        elif v.get('location') == 'CN':
            fl = 0
            for k_lim, discount_share in discounts.items():
                if v.get('volumes') > k_lim:
                    continue
                else:
                    disc = discount_share
                    fl = 1
                    break
            if fl == 0:
                disc = discounts.get(max(discounts.keys()))

            client_price = df['PRICE_USD_CN'].mul((1 - disc)).add(costs.get('CN_LOGISTIC_COST_USD')).round(2)
        print(client_price.head())
        with pd.ExcelWriter(client_price_file_path, engine='xlsxwriter') as writer:
            client_price.to_excel(writer, sheet_name='price')

            # Добавляем график с ценой
            plot_path = f'{client}_wbp.png'
            plt.title('Цена ВБП(DDP)', fontsize=16, fontweight='bold')
            plt.plot(client_price)
            plt.savefig(plot_path)
            plt.close()

            worksheet = writer.sheets['price']
            worksheet.insert_image('C2', plot_path)

        print(f"{client} готов")

    print("Удаляем ненужные файлы")
    for k, v in customers.items():
        if os.path.exists(f"{k}_wbp.png"):
            os.remove(f"{k}_wbp.png")

    print("Работа завершена!")

if __name__ == "__main__":
    calculate_prices()
