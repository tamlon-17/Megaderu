import re
import pandas as pd
from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup
import streamlit as st
import plotly.graph_objs as go
from plotly.subplots import make_subplots

st.set_page_config(page_title='めがで～る 2025', page_icon='icon.ico',
                   initial_sidebar_state='expanded')
st.title('めがで～る 2025')
st.caption('これは、乾田直播の出芽を予測するウェブアプリ（2025年版）です。')
st.caption(
    '予測がはずれても責任は一切取りませんので、ご了承のうえお使いください。')
st.caption('作成者：しがない普及指導員')
st.text('👈👈左側を入力すると、予測結果が変わるよ！！')
st.subheader('予測結果')

# 使用する年を今年に設定
this_year = date.today().year
# アメダス地点をリスト化と辞書化（気象庁の並びで統一）
amedas_l = ['気仙沼', '川渡', '築館', '志津川', '古川', '大衡', '鹿島台',
            '石巻', '新川', '仙台', '白石', '亘理', '米山', '塩釜', '駒ノ湯',
            '丸森', '名取', '蔵王', '女川']
amedas_dic = dict(気仙沼=1, 川渡=2, 築館=3, 志津川=4, 古川=5, 大衡=6, 鹿島台=7,
                  石巻=8, 新川=9, 仙台=10, 白石=11, 亘理=12, 米山=14, 塩釜=15,
                  駒ノ湯=16, 丸森=17, 名取=20, 蔵王=23, 女川=24)

# 西部の市町村をリスト化
east_city = ['泉区', '白石市', '蔵王町', '七ヶ宿町', '川崎町', '大和町',
             '大衡村', '色麻町', '加美町']
# 市町村と気象協会のコードの辞書
city_dic = dict(仙台市=4100, 青葉区=4101, 宮城野区=4102, 若林区=4103,
                太白区=4104, 泉区=4105, 白石市=4206, 角田市=4208, 蔵王町=4301,
                七ヶ宿町=4302, 大河原町=4321, 村田町=4322, 柴田町=4323,
                川崎町=4324, 丸森町=4341, 名取市=4207, 岩沼市=4211, 亘理町=4361,
                山元町=4362, 塩釜市=4203, 多賀城市=4209, 富谷市=4216,
                松島町=4401, 七ヶ浜町=4404, 利府町=4406, 大和町=4421,
                大郷町=4422, 大衡村=4424, 大崎市=4215, 色麻町=4444, 加美町=4445,
                涌谷町=4501, 美里町=4505, 栗原市=4213, 登米市=4212, 石巻市=4202,
                東松島市=4214, 女川町=4581, 気仙沼市=4205, 南三陸町=4606)

# 今日の月日を取得する
today_d = date.today()
# with st.form
# アメダスの地点を入れる
amedas_point = st.sidebar.selectbox('アメダス地点の選択（過去の平均気温）',
                                    amedas_l, index=7)
# アメダスのリストから指定地点のインデックスを取得
amedas_point_i = amedas_l.index(amedas_point)
# 市町村を入れる
city = st.sidebar.selectbox('市町村の選択（天気予報）', city_dic, index=35)
# 播種月日を入れる
seeding_d = st.sidebar.date_input('播種日の入力', date(this_year, 4, 1))

# 播種日が3月１日以前の場合は。播種日を３月１日に補正する。
mar1_day = date(this_year, 3, 1)
seeding_d = seeding_d if (mar1_day < seeding_d) else mar1_day


# 気温の積算は、播種日の翌日から積算を開始すること。
# 播種日から利用日前日までのアメダス平均気温を取得
# アメダスの過去データから指定地点・指定月の日平均気温をリストとして取得する関数
# さらに、リストの取得開始日と終了日も指定できるようにしている。
def scrape_temp(month, s_day, e_day):
    url = (f'http://www.data.jma.go.jp/stats/etrn/view/daily_h1.php?prec_no'
           f'=34&block_no=00&year={this_year}&month={month}&day=&view=p2')
    df = pd.read_html(url)
    tl = list(df[0].iloc[s_day: e_day, amedas_point_i + 1])
    tl1 = [float(re.sub(r'\)', '', a)) if isinstance(a, str) else a for a in tl]
    return tl1


# 降水量取得関数
def scrape_rain(month, s_day, e_day):
    url = (f'http://www.data.jma.go.jp/stats/etrn/view/daily_h1.php?prec_no'
           f'=34&block_no=00&year={this_year}&month={month}&day=&view=p1')
    df = pd.read_html(url)
    rl = list(df[0].iloc[s_day: e_day, amedas_dic[amedas_point]])
    rl = [float(s) if s != '--' else 0.0 for s in rl]
    return rl


# スクレイプする関数を同時に動かす関数
def screpe(month, s_day, e_day):
    tl = scrape_temp(month, s_day, e_day)
    rl = scrape_rain(month, s_day, e_day)
    return tl, rl


# 5月末までしか使えないよ
# 播種日が使用日の前日より前で播種月と使用月が同じ場合
yesterday_d = today_d - timedelta(days=1)
if seeding_d < yesterday_d and seeding_d.month == yesterday_d.month:
    past_t, past_r = screpe(seeding_d.month, seeding_d.day, yesterday_d.day)
# 播種月が使用月より前の場合
elif seeding_d.month < today_d.month:
    past_t, past_r = screpe(seeding_d.month, seeding_d.day, 31)
    sm = seeding_d.month + 1
    # 播種月が使用月の前月の場合
    if sm == today_d.month:
        past_t1, past_r1 = screpe(sm, 0, today_d.day - 1)
        past_t += past_t1
        past_r += past_r1
    # 播種月が使用月の前々月の場合（3月播種-5月使用か4月播種-6月使用）
    else:
        past_t2, past_r2 = screpe(sm, 0, 31)
        past_t += past_t2
        past_r += past_r2
        sm += 1
        past_t3, past_r3 = screpe(sm, 0, today_d.day - 1)
        past_t += past_t3
        past_r += past_r3
# 播種日が使用日より先の場合
else:
    past_t = []
    past_r = []

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


def get_rain(clas_name):
    rsp = soup1.find_all('div', class_=clas_name)
    rlt = [r.text for r in rsp]
    rl = [int(re.sub(r"\D", "", s)) for s in rlt[1:31]]
    return rl


max_tmp_l = get_tmp('high-temp')
min_tmp_l = get_tmp('low-temp')
forecast_r = get_rain('precip')
# 最高気温と最低気温から平均気温を算出すると、0.3度高くなるので、－0.3している
forecast_t = [(x1 + y1) / 2 - 0.3 for (x1, y1) in zip(max_tmp_l, min_tmp_l)]

# CSVから利用日の２週間後からのアメダス平年値を取得
# CSVをデータフレームに代入
df_ave_t = pd.read_csv('temp.csv', encoding='shift_jis')

# 気温のリストの取得開始日（今日の１４日後）を計算
# 2か年平均と５か年平均の2種類のリストを作成する。
start_day = (today_d - date(this_year, 3, 1) + timedelta(days=14))
ave_t2 = list(df_ave_t.iloc[start_day.days:, amedas_point_i + 1])
ave_t5 = list(df_ave_t.iloc[start_day.days:, amedas_point_i + 20])

# 平均気温、降水量の各リストを結合する
combine_t2 = past_t + forecast_t + ave_t2
combine_t5 = past_t + forecast_t + ave_t5
combine_r = past_r + forecast_r
# 播種日より前に使用する場合に、播種日から積算を開始する
if (dd := seeding_d - yesterday_d) >= timedelta():
    combine_t2 = combine_t2[dd.days:]
    combine_t5 = combine_t5[dd.days:]
    combine_r = combine_r[dd.days:]

# 平均気温リストから11.5℃を引いた有効積算リストを作成
valid_t2 = [0 if xx * 10 <= 115 else round(xx - 11.5, 1) for xx in combine_t2]
valid_t5 = [0 if xx * 10 <= 115 else round(xx - 11.5, 1) for xx in combine_t5]


# 積算気温が指定の温度になる日とその時の積算気温を返す関数
def addition_target_temp(vtl, temp):
    t = 0
    s_date = 0
    for i, n in enumerate(vtl, 1):
        t += n
        if t >= temp:
            t = round(t, 1)
            s_date = seeding_d + timedelta(days=i)
            break
    return t, s_date


# 積算30℃、50℃、100℃の日付と温度を取得
temp30_t2, temp30_d2 = addition_target_temp(valid_t2, 30)
temp50_t2, temp50_d2 = addition_target_temp(valid_t2, 50)
temp100_t2, temp100_d2 = addition_target_temp(valid_t2, 100)
temp30_t5, temp30_d5 = addition_target_temp(valid_t5, 30)
temp50_t5, temp50_d5 = addition_target_temp(valid_t5, 50)
temp100_t5, temp100_d5 = addition_target_temp(valid_t5, 100)
# 予測結果の表示
st.text('直近2か年の平均気温（高温年）で予測すると、')
st.text(f'30℃に達するのは、{temp30_d2.month}月{temp30_d2.day}日（{temp30_t2}℃）')
st.text(f'50℃に達するのは、{temp50_d2.month}月{temp50_d2.day}日（{temp50_t2}℃）')
st.text(
    f'100℃に達するのは、{temp100_d2.month}月{temp100_d2.day}日（{temp100_t2}℃）')
st.text('直近5か年の平均気温で予測すると、')
st.text(f'30℃に達するのは、{temp30_d5.month}月{temp30_d5.day}日（{temp30_t5}℃）')
st.text(f'50℃に達するのは、{temp50_d5.month}月{temp50_d5.day}日（{temp50_t5}℃）')
st.text(f'100℃に達するのは、{temp100_d5.month}月{temp100_d5.day}日（{temp100_t5}℃）')

# 積算グラフの表示
# 2つの気温のリストの100までの積算和をリストで
delta_d = temp100_d2 - seeding_d
acu_valid_t2 = [sum(valid_t2[:n + 1]) for n in range(delta_d.days + 1)]
acu_valid_t5 = [sum(valid_t5[:n + 1]) for n in range(delta_d.days + 1)]
# CSVのカラム1から播種日のインデックスを取って、グラフのX軸を作る。
s_i = seeding_d - date(this_year, 3, 1)
df11 = df_ave_t.iloc[s_i.days + 1: s_i.days + delta_d.days + 2, [0]]

df1 = df11.reset_index(drop=True)
df2 = pd.Series(acu_valid_t2)
df3 = pd.Series(acu_valid_t5)
df4 = pd.Series(combine_r)
df_chart = pd.concat([df3, df2, df1, df4], axis=1)
df_chart.columns = ['5か年平均使用', '2か年平均使用', '月日', '降水量']

fig = make_subplots(specs=[[{'secondary_y': True}]])

fig.add_trace(go.Bar(x=df_chart['月日'], y=df_chart['降水量'], name='降水量',
                     marker=dict(color='blue')), secondary_y=True)
fig.add_trace(go.Scatter(x=df_chart['月日'], y=df_chart['5か年平均使用'],
                         name='5か年平均', line=dict(color='yellow')))
fig.add_trace(go.Scatter(x=df_chart['月日'], y=df_chart['2か年平均使用'],
                         name='2か年(高温年）平均', line=dict(color='orange')))

fig.update_layout(xaxis=dict(title='月/日', dtick=5),
                  yaxis1=dict(title='有効積算気温（℃）', range=(0, 110),
                              dtick=10),
                  yaxis2=dict(title='降水量（mm）', range=(0, 27.5), dtick=5,
                              showgrid=False),
                  legend=dict(x=0.05, y=0.95, traceorder='reversed'))

fig.update_layout(shapes=[dict(type='rect', x0=0, x1=delta_d.days, y0=30,
                               y1=50, fillcolor='lightgreen', opacity=0.5,
                               layer='below')])
fig.update_layout(hovermode='x unified')

st.plotly_chart(fig, use_container_width=True)
st.text('降水量は、前日まではアメダスデータ。当日から10日後までは天気予報が表示される。')
