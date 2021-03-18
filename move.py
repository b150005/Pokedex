# インポート文
import requests
from bs4 import BeautifulSoup
import pandas as pd
from PIL import Image
import io

# 技URL
url_move = 'https://yakkun.com/swsh/move_list.htm?mode=all'
res_move = requests.get(url_move)
soup_move = BeautifulSoup(res_move.content, 'html.parser')
soup_info_move = soup_move.find_all('tr', attrs={'class': 'sort_tr'})
soup_info2_move = soup_move.find_all('tr', attrs={'class': 'sort_tr_next'})

# 技情報
data_moves = []

for i in range(len(soup_info_move)):
    # 各技情報
    # ['名前', 'タイプ', '分類', '威力', 'ダイマックス技威力', '命中', 'PP', '直接フラグ(0 == 直接, 1 == 間接)', '守るフラグ(0 == 守れる, 1 == 守れない)', '対象', '効果']

    # 技名
    name_move = soup_info_move[i].find_all('td')[0].text

    # タイプ
    type_move = soup_info_move[i].find_all('td')[1].text

    # 分類
    category_move = soup_info_move[i].find_all('td')[2].text

    # 威力
    # 数値がないとき
    if soup_info_move[i].find_all('td')[3].text.replace('-', '') == '':
        power_move = soup_info_move[i].find_all('td')[3].text.replace('-', '')
    # 数値があるとき
    else:
        power_move = int(soup_info_move[i].find_all('td')[3].text)

    # ダイマックス技威力
    # 数値がないとき
    if soup_info_move[i].find_all('td')[4].text.replace('-', '') == '':
        power_dynamax_move = soup_info_move[i].find_all('td')[4].text.replace('-', '')
    # 数値があるとき
    else:
        power_dynamax_move = int(soup_info_move[i].find_all('td')[4].text)

    # 命中率
    # 数値がないとき
    if soup_info_move[i].find_all('td')[5].text.replace('-', '') == '':
        accuracy_move = soup_info_move[i].find_all('td')[5].text.replace('-', '')
    # 数値があるとき
    else:
        accuracy_move = int(soup_info_move[i].find_all('td')[5].text)

    # PP
    # 数値がないとき
    if soup_info_move[i].find_all('td')[6].text.replace('-', '') == '':
        pp_move = soup_info_move[i].find_all('td')[6].text.replace('-', '')
    # 数値があるとき
    else:
        pp_move = int(soup_info_move[i].find_all('td')[6].text)
    
    # 直接フラグ(0 == 直接, 1 == 間接)
    if '×' in soup_info_move[i].find_all('td')[7].text:
        flg_direct = 1
    if '○' in soup_info_move[i].find_all('td')[7].text:
        flg_direct = 0

    # 守るフラグ(0 == 守れる, 1 == 守れない)
    if '×' in soup_info_move[i].find_all('td')[8].text:
        flg_shield = 1
    if '○' in soup_info_move[i].find_all('td')[8].text:
        flg_shield = 0

    # 対象
    range_move = soup_info2_move[i].find_all('td')[0].text

    # 効果
    effect_move = soup_info2_move[i].find_all('td')[1].text

    # datum_moveの初期化
    datum_move = {}
    
    datum_move['名前'] = name_move
    datum_move['タイプ'] = type_move
    datum_move['分類'] = category_move
    datum_move['威力'] = power_move
    datum_move['ダイマックス技威力'] = power_dynamax_move
    datum_move['命中'] = accuracy_move
    datum_move['PP'] = pp_move
    datum_move['直接'] = flg_direct
    datum_move['守る'] = flg_shield
    datum_move['対象'] = range_move
    datum_move['効果'] = effect_move

    data_moves.append(datum_move)

df2 = pd.DataFrame(data_moves)
df2.to_csv('move.csv', index=False)