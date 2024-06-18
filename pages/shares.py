import streamlit as st
from common import tasks
import pandas as pd

# Title
st.title("Мониторинг портфеля")

# базовые переменные
my = tasks()
dir = my.dir
to_date = pd.to_datetime("2024-06-01")
from_date = to_date - pd.Timedelta(14, "d")


# фильтрация
tickers = st.sidebar.multiselect ("Портфель: ",
                         my.tickers_list, default=my.tickers_list)
 

st.sidebar.header("Период")
from_date = st.sidebar.date_input("с", from_date, format="DD-MM-YYYY")
to_date = st.sidebar.date_input("по", to_date, format="DD-MM-YYYY")

# базовые фреймы
main_df = my.get_news(from_date, to_date)
imoex_df = my.get_imoex(from_date, to_date)
quotes_df = my.get_quotes(from_date, to_date)
shares_pd = my.moex_cb()



"""## Динамика котировок """
import plotly.express as px
for ticker in tickers:
    temp_df = quotes_df[quotes_df["SECID"]==ticker]
    fig = px.line(temp_df, x="TRADEDATE", y="WAPRICE", title=ticker)
    st.plotly_chart(fig)

"""## Посты и тональности """
ticker_df = main_df.loc[main_df["TICKERS"].isin(tickers), : ]
ticker_df["Mood"] = ticker_df["WORDS_lemma"].apply(lambda x: my.mood_text(x))
df = ticker_df[["NEWS_DATE", "CHANNEL", "TICKERS", "NEWS_TEXT", "Mood"]].sort_values(["NEWS_DATE"], ascending=False)

map_color = {"positive":"green", "negative":"red", "neutral":"white"}
df["color"] = df["Mood"].map(map_color)
cols_to_show = ["NEWS_DATE", "TICKERS", "CHANNEL", "NEWS_TEXT"]



text_color = []
n = len(df)
for col in cols_to_show:
    # if col!='NEWS_DATE':
    #     text_color.append(["white"] * n)
    # else:
        text_color.append(df["color"].to_list())

import plotly.graph_objects as go

fig = go.Figure(data=[go.Table(
    header=dict(values=cols_to_show,
                align='left'),
    cells=dict(values=[df["NEWS_DATE"].dt.strftime("%d-%m-%Y"), df.TICKERS, df.CHANNEL,  df.NEWS_TEXT],
               font=dict(color=text_color, size = 15)
               ),
    columnorder = [1,2,3,4],
    columnwidth = [70,50,70,500]
    )
])
fig.update_layout(width=1000,
                  height=2000)


st.plotly_chart(fig)