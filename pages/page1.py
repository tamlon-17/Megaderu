import streamlit as st

st.title('めがで～る Webアプリの説明書')
st.caption('「めがで～る」を使う前に一読してください。')

st.header('アプリの概要')
st.subheader('用途')
st.text('気象データから、乾田直播の出芽時期を予測するアプリ')
st.subheader('使用できる地域')
st.text('宮城県内')
st.subheader('使用可能期間')
st.text('２０２５年３月１日～５月末')
st.subheader('作成者')
st.text('某普及指導員')
st.subheader('免責事項')
st.text('本サイトの利用により発生した損害について、当方は一切責任を負わないものとします')

st.header('使用方法')
st.subheader('必要事項の入力')
st.text('１　予測したい地域のアメダス地点、市町村を選択する')
st.text('２　播種日をカレンダーから選択する')
st.subheader('予測結果の見方')
st.text('有効積算気温が30℃、50℃、100℃に達する日付を表示します')
st.text('直近2か年（高温年）の平均気温と直近5か年の平均気温を使った予測の2つが表示されます')
st.text('グラフは、有効積算気温の累積結果が表示されます')
st.text('青い棒グラフは、過去の降水量と天気予報の降水量が表示されます')

st.header('注意点')
st.text('このアプリはあくまでも気象データから出芽時期を予測するものです')
st.text('実際のほ場では、種もみを掘り起こして、出芽状況を確認してください')

st.header('参照しているデータ')
st.subheader('平均気温')
st.text('前日まで：アメダスデータ')
st.text('当日から14日先：日本気象協会の各市町村の天気予報')
st.text('15日先以降：直近2年間または5年間の平均気温')
st.subheader('降水量')
st.text('前日まで：アメダスデータ')
st.text('当日から10日先：日本気象協会の各市町村の天気予報')

st.header('予測に用いたモデル')
st.text('愛知県農業試験場の不耕起Ｖ溝播種乾田直はの出芽予測モデルを使って予測しています')
st.text('')
if st.button('予測画面に戻る'):
    st.switch_page('./megaderu.py')
