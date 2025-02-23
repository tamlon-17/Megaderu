import pandas as pd
from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup
import streamlit as st
import plotly.express as px

st.set_page_config(page_title='めがで～る 2025')
st.title('めがで～る 2025')
st.caption('これは、乾田直播の出芽を予測するウェブアプリ（2025年版）です。')
st.caption(
    '予測がはずれても責任は一切取りませんので、ご了承のうえお使いください。')
st.caption('作成者：しがない普及指導員')

st.text('👈👈左側を入力すると、予測結果が変わるよ！！')

st.subheader('予測結果')
# 使用する年を今年に設定
this_year = date.today().year
# リストや辞書の定義
# アメダス地点をリスト化（気象庁の並びで統一）
amedas_list = ['気仙沼', '川渡', '築館', '志津川', '古川', '大衡', '鹿島台',
               '石巻', '新川', '仙台', '白石', '亘理', '米山', '塩釜', '駒ノ湯',
               '丸森', '名取', '蔵王', '女川']
# 西部の市町村をリスト化
east_city = ['泉区', '白石市', '蔵王町', '七ヶ宿町', '川崎町', '大和町',
             '大衡村', '色麻町', '加美町']
# 市町村と気象協会のコードの辞書
city_dic = {'仙台市': 4100, '青葉区': 4101, '宮城野区': 4102, '若林区': 4103,
            '太白区': 4104, '泉区': 4105, '白石市': 4206, '角田市': 4208,
            '蔵王町': 4301, '七ヶ宿町': 4302, '大河原町': 4321, '村田町': 4322,
            '柴田町': 4323, '川崎町': 4324, '丸森町': 4341, '名取市': 4207,
            '岩沼市': 4211, '亘理町': 4361, '山元町': 4362, '塩釜市': 4203,
            '多賀城市': 4209, '富谷市': 4216, '松島町': 4401, '七ヶ浜町': 4404,
            '利府町': 4406, '大和町': 4421, '大郷町': 4422, '大衡村': 4424,
            '大崎市': 4215, '色麻町': 4444, '加美町': 4445, '涌谷町': 4501,
            '美里町': 4505, '栗原市': 4213, '登米市': 4212, '石巻市': 4202,
            '東松島市': 4214, '女川町': 4581, '気仙沼市': 4205,
            '南三陸町': 4606}

# 今日の月日を取得する
today_date = date.today()
# with st.form
# アメダスの地点を入れる
amedas_point = st.sidebar.selectbox('アメダス地点の選択（過去の平均気温）',
                                    amedas_list, index=7)
# アメダスのリストから指定地点のインデックスを取得
amedas_point_index = amedas_list.index(amedas_point)
# 市町村を入れる
city = st.sidebar.selectbox('市町村の選択（天気予報）', city_dic, index=35)
# 播種月日を入れる
seeding_date = st.sidebar.date_input('播種日の入力', date(this_year, 4, 1))

# 播種日が3月１日以前の場合は。播種日を３月１日に補正する。
seeding_date = seeding_date if (date(this_year, 3, 1) < seeding_date) \
    else date(this_year, 3, 1)


# 気温の積算は、播種日の翌日から積算を開始すること。
# 播種日から利用日前日までのアメダス平均気温を取得
# アメダスの過去データから指定地点・指定月の日平均気温をリストとして取得する関数
# さらに、リストの取得開始日と終了日も指定できるようにしている。
def scrape_amedas_temp(month, area, s_day, e_day):
    url = (f'http://www.data.jma.go.jp/stats/etrn/view/daily_h1.php?prec_no'
           f'=34&block_no=00&year={this_year}&month={month}&day=&view=p2')
    df = pd.read_html(url)
    temp_list = list(df[0].iloc[s_day: e_day, area + 1])
    return temp_list


# 5月末までしか使えないよ
# 播種日が使用日の前日より前で播種月と使用月が同じ場合
yesterday_date = today_date - timedelta(days=1)
if (seeding_date < yesterday_date and seeding_date.month ==
        yesterday_date.month):
    past_temp = scrape_amedas_temp(seeding_date.month, amedas_point_index,
                                   seeding_date.day, yesterday_date.day)
# 播種月が使用月より前の場合
elif seeding_date.month < today_date.month:
    past_temp = scrape_amedas_temp(seeding_date.month, amedas_point_index,
                                   seeding_date.day, 31)
    sm = seeding_date.month + 1
    # 播種月が使用月の前月の場合
    if sm == today_date.month:
        past_temp += scrape_amedas_temp(sm, amedas_point_index, 0,
                                        today_date.day - 1)
    # 播種月が使用月の前々月の場合（3月播種-5月使用か4月播種-6月使用）
    else:
        past_temp += scrape_amedas_temp(sm, amedas_point_index, 0, 31)
        sm += 1
        past_temp += scrape_amedas_temp(sm, amedas_point_index, 0,
                                        today_date.day - 1)
# 播種日が使用日より先の場合
else:
    past_temp = []

# てんきのサイトから利用日から2週間の予想気温を取得
ew_num = 3420 if city in east_city else 3410
city_num = city_dic[city]
url1 = f'http://tenki.jp/forecast/2/7/{ew_num}/{city_num}/10days.html'
res1 = requests.get(url1)
soup1 = BeautifulSoup(res1.text, 'html.parser')


def get_tmp(clas_name):
    tp = soup1.find_all('span', class_=clas_name)
    tlt = [t.text for t in tp]
    tl = [int(te[:-1]) for te in tlt]
    return tl


max_tmp_list = get_tmp('high-temp')
min_tmp_list = get_tmp('low-temp')
# 最高気温と最低気温から平均気温を算出すると、0.3度高くなるので、－0.3している
forecast_temp = [(x1 + y1) / 2 - 0.3 for (x1, y1) in
                 zip(max_tmp_list, min_tmp_list)]

# CSVから利用日の２週間後からのアメダス平年値を取得
# CSVをデータフレームに代入
df_ave_temp = pd.read_csv('temp.csv', encoding='shift_jis')

# 気温のリストの取得開始日（今日の１４日後）を計算
# 2か年平均と５か年平均の2種類のリストを作成する。
start_day = (today_date - date(this_year, 3, 1) + timedelta(days=14))
ave_temp2 = list(df_ave_temp.iloc[start_day.days:, amedas_point_index + 1])
ave_temp5 = list(df_ave_temp.iloc[start_day.days:, amedas_point_index + 20])

# 平均気温を結合する
combine_temp2 = past_temp + forecast_temp + ave_temp2
combine_temp5 = past_temp + forecast_temp + ave_temp5
# 播種日より前に使用する場合に、播種日から積算を開始する
if (dd := seeding_date - yesterday_date) >= timedelta():
    combine_temp2 = combine_temp2[dd.days:]
    combine_temp5 = combine_temp5[dd.days:]

# 平均気温リストから11.5℃を引いた有効積算リストを作成
valid_temp2 = [0 if xx * 10 <= 115 else round(xx - 11.5, 1) for xx in
               combine_temp2]
valid_temp5 = [0 if xx * 10 <= 115 else round(xx - 11.5, 1) for xx in
               combine_temp5]


# 積算気温が指定の温度になる日とその時の積算気温を返す関数
def addition_target_temp(vtl, temp):
    s_date = 0
    t = 0
    c = 0
    for n in vtl:
        t += n
        c += 1
        if t >= temp:
            t = round(t, 1)
            s_date = seeding_date + timedelta(days=c)
            break
    return t, s_date


# 積算30℃、50℃、100℃の日付と温度を取得
temp30_temp2, temp30_date2 = addition_target_temp(valid_temp2, 30)
temp50_temp2, temp50_date2 = addition_target_temp(valid_temp2, 50)
temp100_temp2, temp100_date2 = addition_target_temp(valid_temp2, 100)
temp30_temp5, temp30_date5 = addition_target_temp(valid_temp5, 30)
temp50_temp5, temp50_date5 = addition_target_temp(valid_temp5, 50)
temp100_temp5, temp100_date5 = addition_target_temp(valid_temp5, 100)
# 予測結果の表示
st.text('直近2か年の平均気温（高温年）で予測すると、')
st.text(
    f'30℃に達するのは、{temp30_date2.month}月{temp30_date2.day}日（{temp30_temp2}℃）')
st.text(
    f'50℃に達するのは、{temp50_date2.month}月{temp50_date2.day}日（{temp50_temp2}℃）')
st.text(f'100℃に達するのは、{temp100_date2.month}月{temp100_date2.day}日'
        f'（{temp100_temp2}℃）')
st.text('直近5か年の平均気温で予測すると、')
st.text(
    f'30℃に達するのは、{temp30_date5.month}月{temp30_date5.day}日（{temp30_temp5}℃）')
st.text(
    f'50℃に達するのは、{temp50_date5.month}月{temp50_date5.day}日（{temp50_temp5}℃）')
st.text(f'100℃に達するのは、{temp100_date5.month}月{temp100_date5.day}日'
        f'（{temp100_temp5}℃）')

# 積算グラフの表示
# 2つの気温のリストの100までの積算和をリストで
delta_date = temp100_date2 - seeding_date
accumulate_valid_temp2 = [sum(valid_temp2[:n + 1]) for n in
                          range(delta_date.days + 1)]
accumulate_valid_temp5 = [sum(valid_temp5[:n + 1]) for n in
                          range(delta_date.days + 1)]
# CSVのカラム1から播種日のインデックスを取って、グラフのX軸を作る。
s_index = seeding_date - date(this_year, 3, 1)
df11 = df_ave_temp.iloc[s_index.days + 1: s_index.days + delta_date.days + 2,
                        [0]]

df1 = df11.reset_index(drop=True)
df2 = pd.Series(accumulate_valid_temp2)

df3 = pd.Series(accumulate_valid_temp5)

df_chart = pd.concat([df3, df2, df1], axis=1)
df_chart.columns = ['5か年平均使用', '2か年平均使用', '月日']
fig = px.line(df_chart, x='月日', y=['5か年平均使用', '2か年平均使用'])
fig.update_layout(xaxis_title='月日', yaxis_title='有効積算気温',
                  legend=dict(x=0.05, y=0.95), legend_traceorder="reversed")
# 背景の特定部分の色を変更
fig.update_layout(shapes=[dict(type='rect', x0=0, x1=delta_date.days, y0=30,
                               y1=50,
                  fillcolor='LightSkyBlue', opacity=0.5, layer='below')])
st.plotly_chart(fig, use_container_width=True)
