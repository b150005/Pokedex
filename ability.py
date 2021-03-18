# インポート文
import requests
from bs4 import BeautifulSoup
import pandas as pd
from PIL import Image
import io

# 特性URL
url_abi = 'https://yakkun.com/swsh/ability_list.htm'
res_abi = requests.get(url_abi)
soup_abi = BeautifulSoup(res_abi.content, 'html.parser')
soup_list_abi = soup_abi.find('table', attrs={'class': 'list'}).find_all('tr')

# 特性リスト
data_abis = []

num = len(soup_list_abi)

for i in list(range(1, num, 1)):
    # datum_abiの初期化
    datum_abi = {}

    # '〜行'でない場合
    if soup_list_abi[i].th is None:
        name_abi = soup_list_abi[i].find_all('td')[0].text
        effect_abi = soup_list_abi[i].find_all('td')[1].text

        datum_abi['特性'] = name_abi
        datum_abi['効果'] = effect_abi
        data_abis.append(datum_abi)
    # '〜行'はスキップ
    else:
        continue

df3 = pd.DataFrame(data_abis)
df3.to_csv('ability.csv', index=False)