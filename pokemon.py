# インポート文
import requests
from bs4 import BeautifulSoup
import pandas as pd
from PIL import Image
import io

# 図鑑一覧URLの定義
url_zukan = 'https://yakkun.com/swsh/zukan/'
res_zukan = requests.get(url_zukan)
# 図鑑一覧URLのHTMLデータ取得
soup_zukan = BeautifulSoup(res_zukan.content, 'html.parser')

# ポケモン名/図鑑No./図鑑URLの取得に必要なデータを抽出
lists_poke = soup_zukan.find('ul', attrs={'class': 'pokemon_list'}).find_all('li')

# 全ポケモンデータ配列の生成
data_poke = []

# 全ポケモンの各データ取得
for list_poke in lists_poke:
    # ポケモン名
    name_poke = list_poke.text.replace('\xa0', '').split(':')[1]
    # 図鑑 No.
    n_zukan_zenkoku_poke = int(list_poke['data-no'])
    # 図鑑URLの末尾
    url_suffix_poke = list_poke.find('a')['href'].replace('/swsh/zukan/', '')
    
    # 図鑑詳細URLの定義
    url_poke = url_zukan + url_suffix_poke
    res_poke = requests.get(url_poke)
    soup_poke = BeautifulSoup(res_poke.content, 'html.parser')
    
    # 各ポケモンのデータ情報
    datum_poke = soup_poke.find('table', attrs={'summary': '基本データ'})
    datum2_poke = soup_poke.find('table', attrs={'class': 'center'})
    list_skill_poke = soup_poke.find('table', attrs={'summary':'技データ'}).find_all('tr')
    
    # 不要な情報を削除
    if datum_poke.find_all('span', attrs={'class':'small'}) != []:
        # 属性無効の'(全く効かない)'を削除
        for _ in range(len(datum_poke.find_all('span', attrs={'class':'small'}))):
            datum_poke.find('span', attrs={'class':'small'}).extract()
    if datum2_poke.find_all('span', attrs={'class':'needless'}) != []:
        # 一部ポケモンの種族値調整・タマゴ歩数情報を削除
        for _ in range(len(datum2_poke.find_all('span', attrs={'class':'needless'}))):
            datum2_poke.find('span', attrs={'class':'needless'}).extract()
    
    # 各ポケモンの画像URLの定義
    url_img_poke = 'https:' + datum_poke.find('img')['src']
    res_img_poke = requests.get(url_img_poke)
    
    # 各ポケモンの画像データ取得
    img_poke = Image.open(io.BytesIO(requests.get(url_img_poke).content))
    img_poke.save(f'../img/{name_poke}.gif')
    
    # 高さ/重さ/タイプ
    for i in range(len(datum_poke.find_all('tr', attrs={'class': 'center'}))):
        if '高さ' in datum_poke.find_all('tr', attrs={'class': 'center'})[i].text:
            # 高さ
            height_poke = float(datum_poke.find_all('tr', attrs={'class': 'center'})[i].text.replace('高さ', '').replace('m', ''))
        if '重さ' in datum_poke.find_all('tr', attrs={'class': 'center'})[i].text:
            # 重さ
            weight_poke = float(datum_poke.find_all('tr', attrs={'class': 'center'})[i].text.replace('重さ', '').split('kg')[0])
        if 'タイプ' in datum_poke.find_all('tr', attrs={'class': 'center'})[i].text:
            # タイプ
            types_poke = []
            for j in range(len(datum_poke.find_all('tr', attrs={'class': 'center'})[i].find_all('img'))):
                types_poke.append(datum_poke.find_all('tr', attrs={'class': 'center'})[i].find_all('img')[j]['alt'])
        
    # 英語名
    for i in range(len(datum_poke.find_all('tr', attrs={'class': 'center'}))):
        if datum_poke.find_all('tr', attrs={'class': 'center'})[i].text.startswith('英語名'):
            engName_poke = datum_poke.find_all('tr', attrs={'class': 'center'})[i].text.replace('英語名', '')
    
    # weak/strong
    advs_poke = []     # 効果ばつぐん(有利対面)
    disAdvs_poke = []  # 効果いまひとつ(不利対面)

    for i in range(len(datum_poke.find_all('ul', attrs={'class': 'type'})[1].find_all('li'))):
        if float(datum_poke.find_all('ul', attrs={'class': 'type'})[1].find_all('li')[i].find_all('img')[1]['alt'].replace('倍', '')) < 1.0:
            advs_poke.append(datum_poke.find_all('ul', attrs={'class': 'type'})[1].find_all('li')[i].find('img')['alt'])
        elif float(datum_poke.find_all('ul', attrs={'class': 'type'})[1].find_all('li')[i].find_all('img')[1]['alt'].replace('倍', '')) >= 1.0:
            disAdvs_poke.append(datum_poke.find_all('ul', attrs={'class': 'type'})[1].find_all('li')[i].find('img')['alt'])
        
    # 進化リスト
    unordered_lists_names_evo_poke = []  # 進化ポケモンリスト(重複あり)
    lists_names_evo_poke = []  # 進化ポケモンリスト(重複なし)
    redundant_conds_evo_poke = ['なし']  # 進化条件(不要な情報を含む)
    conds_evo_poke = ['なし']  # 進化条件(不要な情報を含まない)

    # 進化先がない場合
    if datum_poke.find_all('ul', attrs={'class':'evo_list'}) == []:
        lists_names_evo_poke.append(name_poke)
    # 進化先がある場合
    else:
        # evo_arrowの削除
        for _ in range(len(datum_poke.find('ul', attrs={'class':'evo_list'}).find_all('li', attrs={'class':'evo_arrow'}))):
            datum_poke.find('ul', attrs={'class':'evo_list'}).find('li', attrs={'class':'evo_arrow'}).extract()

        # 進化ポケモンリスト
        for i in range(len(datum_poke.find('ul', attrs={'class':'evo_list'}).find_all('img'))):
            # 進化系統を進化元ポケモン含めて取得
            unordered_lists_names_evo_poke.append(datum_poke.find('ul', attrs={'class':'evo_list'}).find_all('img')[i]['alt'])

        # 進化元ポケモンがリスト内に複数ある場合
        if unordered_lists_names_evo_poke.count(unordered_lists_names_evo_poke[0]) >= 2:
            num = len(unordered_lists_names_evo_poke)
            # リスト内のポケモンの数を調整
            for j in range(num - 1):
                # 進化先ポケモンリストで進化元ポケモンが重複する場合(後ろから走査)
                if unordered_lists_names_evo_poke[num - 1 - j] == unordered_lists_names_evo_poke[0]:
                    # 進化元ポケモンの重複を削除
                    del unordered_lists_names_evo_poke[num - 1 - j]

            lists_names_evo_poke = unordered_lists_names_evo_poke
            # 例: ['ケムッソ', 'マユルド', 'アゲハント', 'カラサリス', 'ドクケイル']
        # 進化元ポケモンがリスト内に単一である場合
        else:
            # 進化先ポケモンの重複を削除
            lists_names_evo_poke = sorted(set(unordered_lists_names_evo_poke), key=unordered_lists_names_evo_poke.index)

        # a要素(ポケモン名)を削除
        for _ in range(len(datum_poke.find('ul', attrs={'class':'evo_list'}).find_all('a'))):
            datum_poke.find('ul', attrs={'class':'evo_list'}).a.extract()

        # 進化条件(進化元ポケモンに条件はないので'-1')
        for i in range(len(datum_poke.find('ul', attrs={'class':'evo_list'}).find_all('li')) - 1):
            # 進化条件の抜き出し('⇒'と'\xa0(半角スペース)'を削除)
            redundant_conds_evo_poke.append(datum_poke.find('ul', attrs={'class':'evo_list'}).find_all('li')[1 + i].text.replace('⇒', '').replace('\xa0', ''))
            # 第7世代以前の情報は削除('【'で始まる情報は削除)
            conds_evo_poke = [cond for cond in redundant_conds_evo_poke if not cond.startswith('【')]

        # 進化条件リストの2番目以降のインデックスの空文字を削除(後ろから走査)
        num = len(conds_evo_poke)
        for i in range(num - 1):
            if conds_evo_poke[num - 1 - i] == '':
                del conds_evo_poke[num - 1 - i]
    
    # 種族値
    stats_base_poke = []
    # [H, A, B, C, D, S, Ave., Tot.]
    for i in range(6):
        stats_base_poke.append(int(datum2_poke.find_all('td')[2 * i + 1].text.lstrip()))

    stats_base_poke.append(float(datum2_poke.find_all('td')[13].text.split('\xa0')[1]))
    stats_base_poke.append(int(datum2_poke.find_all('td')[13].text.split('\xa0')[3]))
    
    # 実数値
    # [max, semi-max, intact, semi-min, min]
    stats_h_poke = []  # HP
    stats_a_poke = []  # 攻撃
    stats_b_poke = []  # 防御
    stats_c_poke = []  # 特攻
    stats_d_poke = []  # 特防
    stats_s_poke = []  # 素早さ

    for i in range(5):
        stats_h_poke.append(int(datum2_poke.find_all('td')[15 + i].text))
        stats_a_poke.append(int(datum2_poke.find_all('td')[21 + i].text))
        stats_b_poke.append(int(datum2_poke.find_all('td')[27 + i].text))
        stats_c_poke.append(int(datum2_poke.find_all('td')[33 + i].text))
        stats_d_poke.append(int(datum2_poke.find_all('td')[39 + i].text))
        stats_s_poke.append(int(datum2_poke.find_all('td')[45 + i].text))
        
    # 性別割合
    rate_sex_poke = datum2_poke.find_all('td')[75].text.replace('\xa0', ' ')
    # タマゴグループ
    eggGroup_poke = datum2_poke.find_all('td')[79].text.replace('\xa0', ' ')
    
    # 特性, 夢特性
    abi_poke = []
    abi_hid_poke = []

    for i in range(28, len(datum2_poke.find_all('td', attrs={'class': 'c1'}))):
        # 夢特性(文字列の最初に'*'を含む場合)
        if '*' in datum2_poke.find_all('td', attrs={'class': 'c1'})[i].text:
            abi_hid_poke.append(datum2_poke.find_all('td', attrs={'class': 'c1'})[i].text.replace('*', ''))
        # 特性
        else:
            # '野生が持っている道具'を削除
            if '確率' in datum2_poke.find_all('td', attrs={'class': 'c1'})[i].text:
                continue
            else:
                abi_poke.append(datum2_poke.find_all('td', attrs={'class': 'c1'})[i].text.replace('*', ''))

   # 技リスト
    j = 0
    k = 0
    l = 0
    m = 0
    n = 0
    o = 0
    p = 0
    q = 0
    r = 0
    s = 0

    # 不要な行を削除(後ろから走査)
    # numの初期化
    num = len(list_skill_poke)
    lst_index = []
    # 進化前のときだけ覚える技が複数パターンある場合(スピアーなど)
    for i in range(num):
        if 'の時だけ覚える技' in list_skill_poke[num - 1 - i].text:
            # lst_ indexには後ろのインデックスから追加
            lst_index.append(num - 1 - i)
            # 進化前のときだけ覚える技が複数パターンある場合(スピアーなど)の削除
            # -> 最初の'進化前『~』の時だけ覚える技'のみ残す
    if len(lst_index) >= 2:
        for h in range(len(lst_index) - 1):
            del list_skill_poke[lst_index[h]]
    # numの初期化
    num = len(list_skill_poke)
    # 空白行、'※'から始まる行の削除
    for i in range(num):
        if list_skill_poke[num - 1 - i].text == '':
            del list_skill_poke[num - 1 - i]
        if list_skill_poke[num - 1 - i].text.startswith('※'):
            del list_skill_poke[num - 1 - i]

    for i in range(len(list_skill_poke)):
        if 'レベルアップで覚える技' in list_skill_poke[i].text:
            j = i
        if '◆\xa0わざマシンで覚える技' in list_skill_poke[i].text:
            k = i
        if '◆\xa0わざレコードで覚える技' in list_skill_poke[i].text:
            l = i
        if 'タマゴ技' in list_skill_poke[i].text and '◆\xa0' in list_skill_poke[i].text:
            m = i
        if '◆\xa0教え技' in list_skill_poke[i].text:
            n = i
        if '◆\xa0特別な技' in list_skill_poke[i].text:
            o = i
        if 'の時だけ覚える技' in list_skill_poke[i].text:
            p = i
        if '◆\xa0配布限定の特別な技' in list_skill_poke[i].text:
            q = i
        if '◆\xa0過去作でしか覚えられない技' in list_skill_poke[i].text:
            r = i
        if '◆\xa0過去の配布限定の特別な技' in list_skill_poke[i].text:
            s = i
    
    num_list = [j, k, l, m, n, o, p, q, r, s]
    num = len(num_list)

    # 0をリストから削除
    for i in range(num):
        if num_list[num - 1 - i] == 0:
            del num_list[num - 1 - i]
    # num_listの順番をソート
    num_list.sort()

    # レベルアップで覚える技
    skill_lvup_poke = []
    if j == 0:
        # {'わざ':'Lv'}
        dic_skill_lvup_poke = {}
        # nxtの定義
        for i in range(len(num_list)):
            if num_list[i] > j:
                nxt = num_list[i]
                break
        # 各種技リストに格納
        for i in range(0, len(list_skill_poke))[j + 2: nxt: 2]:
            dic_skill_lvup_poke[f"{list_skill_poke[i].find_all('td')[1].text.replace('New','').replace('!', '')}"] = list_skill_poke[i].find_all('td')[0].text
        skill_lvup_poke.append(dic_skill_lvup_poke)

    # わざマシンで覚える技
    skill_machine_poke = []
    if k != 0:
        # nxtの定義
        for i in range(len(num_list)):
            if num_list[i] > k:
                nxt = num_list[i]
                break
        # 各種技リストに格納
        for i in range(0, len(list_skill_poke))[k + 1: nxt if k < nxt else len(list_skill_poke): 2]:
            if list_skill_poke[i].text == 'なし':
                break
            else:
                skill_machine_poke.append(list_skill_poke[i].find_all('td')[1].text.replace('New','').replace('!', ''))

    # わざレコードで覚える技
    skill_record_poke =  []
    if l != 0:
        # nxtの定義
        for i in range(len(num_list)):
            if num_list[i] > l:
                nxt = num_list[i]
                break
        # 各種技リストに格納
        for i in range(0, len(list_skill_poke))[l + 1: nxt if l < nxt else len(list_skill_poke): 2]:
            if list_skill_poke[i].text == 'なし':
                break
            else:
                skill_record_poke.append(list_skill_poke[i].find_all('td')[1].text.replace('New','').replace('!', ''))

    # たまご技
    skill_egg_poke = []
    if m != 0:
        # nxtの定義
        for i in range(len(num_list)):
            if num_list[i] > m:
                nxt = num_list[i]
                break
        # 各種技リストに格納
        for i in range(0, len(list_skill_poke))[m + 1: nxt if m < nxt else len(list_skill_poke): 2]:
            if list_skill_poke[i].text == 'なし':
                break
            else:
                skill_egg_poke.append(list_skill_poke[i].find_all('td')[1].text.replace('New','').replace('!', '').split('[')[0])

    # 教え技
    skill_learn_poke = []
    if n != 0:
        # {'わざ':'バージョン'}
        dic_skill_learn_poke = {}
        # nxtの定義
        for i in range(len(num_list)):
            if num_list[i] > n:
                nxt = num_list[i]
                break
        # 各種技リストに格納
        for i in range(0, len(list_skill_poke))[n + 1: nxt if n < nxt else len(list_skill_poke): 2]:
            if list_skill_poke[i].text == 'なし':
                break
            else:
                dic_skill_learn_poke[f"{list_skill_poke[i].find_all('td')[1].text.replace('New','').replace('!', '')}"] = list_skill_poke[i].find_all('td')[0].text
        skill_learn_poke.append(dic_skill_learn_poke)
                
    # 特別な技
    skill_special_poke = []
    if o != 0:
        # {'わざ':'種別'}
        dic_skill_special_poke = {}
        # nxtの定義
        for i in range(len(num_list)):
            if num_list[i] > o:
                nxt = num_list[i]
                break
        # 各種技リストに格納
        for i in range(0, len(list_skill_poke))[o + 1: nxt if o < nxt else len(list_skill_poke): 2]:
            if list_skill_poke[i].text == 'なし':
                break
            else:
                dic_skill_special_poke[f"{list_skill_poke[i].find_all('td')[1].text.replace('New','').replace('!', '')}"] = list_skill_poke[i].find_all('td')[0].text.replace('キョ', 'キョダイマックス技')
        skill_special_poke.append(dic_skill_special_poke)

    # 進化前のみ覚える技
    skill_onbase_poke = []
    if p != 0:
        # {'わざ':'条件'}
        dic_skill_onbase_poke = {}
        # nxtの定義
        for i in range(len(num_list)):
            if num_list[i] > p:
                nxt = num_list[i]
                break
        # 各種技リストに格納
        for i in range(0, len(list_skill_poke))[p + 1: nxt if p < nxt else len(list_skill_poke): 2]:
            if list_skill_poke[i].text == 'なし':
                break
            else:
                dic_skill_onbase_poke[f"{list_skill_poke[i].find_all('td')[1].text.replace('New','').replace('!', '')}"] = list_skill_poke[i].find_all('td')[0].text
        skill_onbase_poke.append(dic_skill_onbase_poke)

    # 配布限定の特別な技
    skill_gifted_poke = []
    if q != 0:
        # nxtの定義
        for i in range(len(num_list)):
            if num_list[i] > q:
                nxt = num_list[i]
                break
        # 各種技リストに格納
        for i in range(0, len(list_skill_poke))[q + 1: nxt if q < nxt else len(list_skill_poke): 2]:
            # {'わざ':'条件'}
            dic_skill_gifted_poke = {}
            list_events = []
            for j in range(len(list_skill_poke[i].text.replace(']', '').split('[')[1].split(','))):
                list_events.append(list_skill_poke[i].text.replace(']', '').split('[')[1].split(',')[j])
            dic_skill_gifted_poke[f"{list_skill_poke[i].text.replace(']', '').split('[')[0]}"] = list_events
            skill_gifted_poke.append(dic_skill_gifted_poke)

    # 過去作でしか覚えられない技
    skill_past_poke = []
    if r != 0:
        # nxtの定義
        for i in range(len(num_list)):
            if num_list[i] > r:
                nxt = num_list[i]
                break
        # 各種技リストに格納
        for i in range(0, len(list_skill_poke))[r + 1: nxt if r < nxt else len(list_skill_poke): 2]:
            # {'わざ':'バージョン'}
            dic_skill_past_poke = {}
            list_versions = []
            for j in range(len(list_skill_poke[i].text.replace(']', '').split('[')[1].split(','))):
                list_versions.append(list_skill_poke[i].text.replace(']', '').split('[')[1].split(',')[j])
            dic_skill_past_poke[f"{list_skill_poke[i].text.replace(']', '').split('[')[0]}"] = list_versions
            skill_past_poke.append(dic_skill_past_poke)

    # 過去の配布限定の特別な技
    skill_gifted_past_poke = []
    if s != 0:
        # nxtの定義
        for i in range(len(num_list)):
            if num_list[i] > s:
                nxt = num_list[i]
                break
        # 各種技リストに格納
        for i in range(0, len(list_skill_poke))[s + 1: nxt if s < nxt else len(list_skill_poke): 2]:
            # {'わざ':'条件'}
            dic_skill_gifted_past_poke = {}
            list_past_events = []
            for j in range(len(list_skill_poke[i].text.replace(']', '').split('[')[1].split(','))):
                list_past_events.append(list_skill_poke[i].text.replace(']', '').split('[')[1].split(',')[j])
            dic_skill_gifted_past_poke[f"{list_skill_poke[i].text.replace(']', '').split('[')[0]}"] = list_past_events
            skill_gifted_past_poke.append(dic_skill_gifted_past_poke)
                
    # 各種データを格納した辞書
    datum_data_poke = {}
    
    datum_data_poke['ポケモン名'] = name_poke
    datum_data_poke['英語名'] = engName_poke
    datum_data_poke['全国図鑑No.'] = n_zukan_zenkoku_poke
    datum_data_poke['高さ'] = height_poke
    datum_data_poke['重さ'] = weight_poke
    datum_data_poke['タイプ'] = types_poke
    datum_data_poke['有利'] = advs_poke
    datum_data_poke['不利'] = disAdvs_poke
    datum_data_poke['進化リスト'] = lists_names_evo_poke
    datum_data_poke['進化条件'] = conds_evo_poke
    datum_data_poke['種族値'] = stats_base_poke
    datum_data_poke['実数値h'] = stats_h_poke
    datum_data_poke['実数値a'] = stats_a_poke
    datum_data_poke['実数値b'] = stats_b_poke
    datum_data_poke['実数値c'] = stats_c_poke
    datum_data_poke['実数値d'] = stats_d_poke
    datum_data_poke['実数値s'] = stats_s_poke
    datum_data_poke['性別割合'] = rate_sex_poke
    datum_data_poke['タマゴグループ'] = eggGroup_poke
    datum_data_poke['特性'] = abi_poke
    datum_data_poke['夢特性'] = abi_hid_poke
    datum_data_poke['レベルアップで覚える技'] = skill_lvup_poke
    datum_data_poke['わざマシンで覚える技'] = skill_machine_poke
    datum_data_poke['わざレコードで覚える技'] = skill_record_poke
    datum_data_poke['たまご技'] = skill_egg_poke
    datum_data_poke['教え技'] = skill_learn_poke
    datum_data_poke['特別な技'] = skill_special_poke
    datum_data_poke['進化前のみ覚える技'] = skill_onbase_poke
    datum_data_poke['配布限定の特別な技'] = skill_gifted_poke
    datum_data_poke['過去作でしか覚えられない技'] = skill_past_poke
    datum_data_poke['過去の配布限定の特別な技'] = skill_gifted_past_poke
    
    data_poke.append(datum_data_poke)

df = pd.DataFrame(data_poke)
df = df[['全国図鑑No.', 'ポケモン名', '英語名', '高さ', '重さ', 'タイプ', '有利', '不利', '進化リスト',
       '進化条件', '種族値', '実数値h', '実数値a', '実数値b', '実数値c', '実数値d', '実数値s', '性別割合',
       'タマゴグループ', '特性', '夢特性', 'レベルアップで覚える技', 'わざマシンで覚える技', 'わざレコードで覚える技',
       'たまご技', '教え技', '特別な技', '進化前のみ覚える技', '配布限定の特別な技', '過去作でしか覚えられない技',
       '過去の配布限定の特別な技']]
df.to_csv('pokemon.csv', index=False)