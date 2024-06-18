import streamlit as st
from common import tasks
import pandas as pd
import plotly.express as px

# Title
st.title("Статистика корпуса")

# базовые переменные
my = tasks()
dir = my.dir
to_date = pd.to_datetime("2024-06-01")
from_date = to_date - pd.Timedelta(14, "d")


st.sidebar.header("Период")
from_date = st.sidebar.date_input("с", from_date, format="DD-MM-YYYY")
to_date = st.sidebar.date_input("по", to_date, format="DD-MM-YYYY")

# базовые фреймы
main_df = my.get_news(from_date, to_date)
imoex_df = my.get_imoex(from_date, to_date)
quotes_df = my.get_quotes(from_date, to_date)
shares_pd = my.moex_cb()

"""## Воронка новостей """
data = dict(
    number=[len(main_df), 
            main_df[(main_df["TICKERS"].str.len()>2)]["TICKERS"].count(), 
            main_df[(main_df["TICKERS"].str.len()>2) & (main_df["TICKERS"].str.len()<5)]["TICKERS"].count()],
    stage=["Всего постов", "С тикерами", "С одним тикером"])
fig = px.funnel(data, x='number', y='stage')

st.plotly_chart(fig)

"""## Каналы"""
# This dataframe has 244 lines, but 4 distinct values for `day`
df = main_df.groupby([pd.Grouper(key='CHANNEL')]).agg('count')
df.reset_index(inplace=True)
fig = px.pie(df, values='NEWS_TEXT', names='CHANNEL',
             color_discrete_sequence=px.colors.sequential.RdBu)
fig.update_traces(textposition='inside', textinfo='value+label', showlegend = False)
st.plotly_chart(fig)