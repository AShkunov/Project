import streamlit as st
from common import tasks
import pandas as pd

# Title
st.title("Лингвистические компоненты мониторинга фондового рынка")

# базовые переменные
my = tasks()
dir = my.dir
to_date = pd.to_datetime("2024-06-01")
from_date = to_date - pd.Timedelta(14, "d")


# фильтрация
st.sidebar.header("Период")
from_date = st.sidebar.date_input("с", from_date, format="DD-MM-YYYY")
to_date = st.sidebar.date_input("по", to_date, format="DD-MM-YYYY")

# базовые фреймы
main_df = my.get_news(from_date, to_date)
imoex_df = my.get_imoex(from_date, to_date)
quotes_df = my.get_quotes(from_date, to_date)
shares_pd = my.moex_cb()


"""## Imoex и посты """
# st.header()
import plotly.graph_objects as go
from plotly.subplots import make_subplots 

groupNews = main_df.groupby("NEWS_DATE").size().to_frame(name = 'count').reset_index()
fig = make_subplots(specs=[[{"secondary_y": True}]])
# задаем отображение количества новостей
fig.add_trace(
    go.Bar(
        name = "Количество постов",
        x=groupNews["NEWS_DATE"], y=groupNews["count"],
        marker=dict(color="lightsteelblue"),
        opacity=0.5,
    ),
    secondary_y=True
)
# задаем отображение динамики индекса
fig.add_trace(
    go.Candlestick(
        name = "Цена IMOEX",
        x=imoex_df['Date'],
        open=imoex_df['Open'],
        high=imoex_df['High'],
        low=imoex_df['Low'],
        close=imoex_df['Open']+(imoex_df['Open']/100*imoex_df['Change']),
    ),
    secondary_y=False
)
# добавляем заголовок
# fig.update_layout(title = 'Динамика <b>IMOEX</b>', xaxis_rangeslider_visible=False)
fig.update_layout(xaxis_rangeslider_visible=False)

st.plotly_chart(fig)

""" ## Колебания котировок """
quotes_df.sort_values(by="TRADEDATE", ascending=True, inplace=True)
# tickers_list = my.tickers_list
tickers_list = pd.unique(quotes_df["SECID"])
limit = 0.1 # отклонение цены от скользящего среднего (%/100). При 0 отображаются все
stat_df = my.quotes_stat(tickers_list, quotes_df)
# отбор среди списка моих акций с отклонением выше порогового
stat_df = stat_df[(stat_df["DEV"]>=limit) | (stat_df["DEV"]<=-limit)]
stat_group = stat_df.groupby(by = ["SECID"])[["SECID"]].count().rename_axis(["TICKER"])
stat_group.reset_index(inplace=True)
stat_group = pd.merge(
    stat_group, shares_pd, left_on=["TICKER"], right_on=["TRADE_CODE"], how="left"
)
stat_group.drop("TRADE_CODE", axis = 1, inplace=True)
stat_group.rename(columns = {'SECID':'count'}, inplace = True )

import plotly.express as px
fig = px.treemap(stat_group,
                 path=['TICKER'],
                 values='count',
                 labels="count",
                 color="count",
                 color_continuous_scale='RdYlGn_r'
                 )
fig.update_layout(title="Отклонения от средневзвешенной цены на "+str(limit*100)+"%",
                #   width=1000,
                #   height=700,
                  font_size = 14)

st.plotly_chart(fig)

""" ## Ключевые слова """
from wordcloud import WordCloud
import matplotlib.pyplot as plt

text_forBOW = main_df["WORDS_lemma"].values.astype(str)

plt.figure(figsize=(10, 10))
plt.imshow(WordCloud(width = 3000, 
                    height = 2000,
                    max_words = 20,
                    stopwords = ["компания", "акция", "идея", "наш"], 
                    random_state=1, 
                    background_color='black', 
                    margin=20, 
                    colormap='Pastel1', 
                    collocations=False).generate(" ".join(text_forBOW))) 
plt.axis("off")
st.pyplot(plt)

""" ## Суммаризация новостей """
from nltk.tokenize import sent_tokenize, RegexpTokenizer
from nltk.stem.snowball import RussianStemmer
import networkx as nx
from itertools import combinations

# суммаризация текста
def similarity(s1, s2):
    if not len(s1) or not len(s2):
        return 0.0
    return len(s1.intersection(s2))/(1.0 * (len(s1) + len(s2)))
# Выдает список предложений отсортированных по значимости
def textrank(text):
    sentences = sent_tokenize(text)
    tokenizer = RegexpTokenizer(r'\w+')
    lmtzr = RussianStemmer()
    words = [set(lmtzr.stem(word) for word in tokenizer.tokenize(sentence.lower()))
             for sentence in sentences] 	 
    pairs = combinations(range(len(sentences)), 2)
    scores = [(i, j, similarity(words[i], words[j])) for i, j in pairs]
    scores = filter(lambda x: x[2], scores)
    g = nx.Graph()
    g.add_weighted_edges_from(scores)
    pr = nx.pagerank(g)
    return sorted(((i, pr[i], s) for i, s in enumerate(sentences) if i in pr), key=lambda x: pr[x[0]], reverse=True)
# Сокращает текст до нескольких наиболее важных предложений
def sumextract(text, n=5):
    tr = textrank(text)
    top_n = sorted(tr[:n])
    return ' '.join(x[2] for x in top_n)

group_news = main_df.groupby('NEWS_DATE', group_keys=True)[["NEWS_TEXT"]].agg(lambda x: ','.join(x))
group_news["Summary"] = group_news["NEWS_TEXT"].apply(sumextract)
group_news = group_news.drop("NEWS_TEXT", axis=1)
group_news.reset_index(inplace=True)
group_news["NEWS_DATE"] = pd.to_datetime(group_news["NEWS_DATE"]).dt.strftime("%d-%m-%Y")
df = group_news[["NEWS_DATE", "Summary"]].sort_values(["NEWS_DATE"], ascending=False)


import plotly.graph_objects as go

fig = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns),
                align='left'),
    cells=dict(values=[df.NEWS_DATE, df.Summary],
               align='left'
               ),
    columnorder = [1,2],
    columnwidth = [70,400],
    )
])
fig.update_traces(cells_font=dict(size = 15))
fig.update_layout(width=1000,
                  height=2000)

st.plotly_chart(fig)