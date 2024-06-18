class tasks:
    import pandas as pd
    import spacy
    from textblob import TextBlob

    def __init__(self):
        self.dir = "D:\\Develop\VS\HSE\Pump_Dump\\"  # папка проекта
        self.tickers_list = ["sber", "gazp", "lkoh"]
        self.nlp = self.spacy.load("ru_core_news_lg") 

    # def dflist_to_text(self, words): # форматирование столбцов со списочными значениями
    #     text = ','.join(words)
    #     text = text.replace("[","")
    #     text = text.replace("]","")
    #     text = text.replace(","," ")
    #     text = text.replace("'","")
    #     return text
    
    # def dfstring_to_text(self, text): # форматирование ячейки со списочными значениями
    #     text = text.replace("[","")
    #     text = text.replace("]","")
    #     text = text.replace(",","")
    #     text = text.replace("'","")
    #     return text
    
    def moex_cb(self):
        pd = self.pd
        shares_pd = pd.read_csv(self.dir + "Market\\moex_cb.csv", encoding="utf-8")
        shares_pd = shares_pd[(shares_pd["SUPERTYPE"] == "Акции")]
        shares_pd.dropna(subset="INN", axis=0, inplace=True)
        # удаляем строки без тикеров
        shares_pd.dropna(subset="TRADE_CODE", axis=0, inplace=True)
        # Тикеры к нижнему регистру
        shares_pd["TRADE_CODE"] = shares_pd["TRADE_CODE"].str.lower()
        shares_pd["LIST_SECTION"] = shares_pd["LIST_SECTION"].str.replace(" уровень", "")
        shares_pd = shares_pd[["TRADE_CODE", "LIST_SECTION"]]
        shares_pd.head()
        return shares_pd


    def quotes_df(self): # загрузка истории котировок
        pd = self.pd
        quotes_df = pd.read_csv(self.dir + "Answers\\alltickers.csv", encoding="utf-8", sep="|", index_col=0)
        quotes_df["TRADEDATE"] = pd.to_datetime(quotes_df["TRADEDATE"])
        return quotes_df
    
    def get_quotes(self, from_date, to_date): # загрузка истории котировок в интервале дат
        pd = self.pd
        quotes_df = self.quotes_df()
        quotes_df.dropna(inplace=True)
        quotes_df = quotes_df[
            (quotes_df["TRADEDATE"] >= pd.to_datetime(from_date)) &
            (quotes_df["TRADEDATE"] <= pd.to_datetime(to_date))
            ].sort_values(by="TRADEDATE", ascending=False)
        return quotes_df
    
    def quotes_stat(self, tickers_list, df): # расчет скользящего среднего и отклонения от него по списку тикеров
        pd = self.pd
        pd.options.mode.chained_assignment = None
        tic_quot_df = pd.DataFrame()
        for ticker in tickers_list:
            temp_df = df.loc[df["SECID"]==ticker]
            tic_quot_df = pd.concat([tic_quot_df, temp_df])
        return tic_quot_df

    def news_df(self): # загрузка новостей
        pd = self.pd
        main_df = pd.read_csv(self.dir + "Answers\\news_quotes.csv", encoding="utf-8", sep="|", index_col=0)
        main_df["NEWS_DATE"] = pd.to_datetime(main_df["NEWS_DATE"])
        return main_df

    def get_news(self, from_date, to_date):
        pd = self.pd
        main_df = self.news_df()
        return main_df[
            (main_df["NEWS_DATE"] >= pd.to_datetime(from_date)) &
            (main_df["NEWS_DATE"] <= pd.to_datetime(to_date))
            ].sort_values(by="NEWS_DATE", ascending=False)
    
    def get_imoex(self, from_date, to_date):
        pd = self.pd
        imoex_df = self.imoex_df()
        return imoex_df[
            (imoex_df["Date"] >= pd.to_datetime(from_date)) &
            (imoex_df["Date"] <= pd.to_datetime(to_date))
            ].sort_values(by="Date", ascending=False)


    def imoex_df(self):# загрузка котировок IMOEX
        pd = self.pd
        # загружаем фрейм с котировками индекса IMOEX
        imoex_path = self.dir + "Market\\MOEX Russia Historical Data.csv"
        imoex_df = pd.read_csv(
            imoex_path,
            encoding="utf-8",
            keep_default_na=False,
        )
        # удаляем лишние столбцы и символы в названиях столбцов
        imoex_df.rename(columns={"Change %":"Change"},inplace=True)
        imoex_df["Change"] = imoex_df["Change"].str.replace('%', '')
        imoex_df.drop('Vol.', axis= 1 , inplace= True )
        imoex_df["Date"] = imoex_df["Date"].astype("datetime64[ns]")
        # формируем корректные для обработки значения для числовых столбцов
        cols_float=["Price", "Low", "Open", "High", "Change"]
        imoex_df[cols_float] = imoex_df[cols_float].apply(lambda x: x.str.replace(",", ""))
        imoex_df[cols_float] = imoex_df[cols_float].apply(pd.to_numeric)
        # рассчитываем дату закрытия
        imoex_df["Close"] = (imoex_df['Open']+(imoex_df['Open']/100*imoex_df['Change'])).round(2)
        imoex_df.sort_values(by="Date")
        return imoex_df

    def mood_text(self, text):
        # Используем TextBlob для анализа тональности
        analysis = self.TextBlob(text)
        sentiment = analysis.sentiment.polarity
        if sentiment > 0:
            sentiment_label = "positive"
        elif sentiment < 0:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        return sentiment_label




# МЕГА КОРПУС
# import pandas as pd
# import os
# dir = "D:\\Develop\\VS\\HSE\\News\\TGData\\"
# files = [_ for _ in os.listdir(dir) if _.endswith(r".csv")]
# df_temp = pd.DataFrame()
# for file in files:
#     print(dir + file)
#     temp_df = pd.read_csv(dir + file, encoding="utf-8", sep="|")
#     df_temp = pd.concat([df_temp, temp_df])

# import plotly.express as px
# # This dataframe has 244 lines, but 4 distinct values for `day`
# df = df_temp.groupby([pd.Grouper(key='CHANNEL')]).agg('count')
# df.reset_index(inplace=True)
# df
# fig = px.pie(df, values='NEWS_TEXT', names='CHANNEL',
#              color_discrete_sequence=px.colors.sequential.RdBu)
# fig.update_traces(textposition='inside', textinfo='value+label', showlegend = False)
# fig.show()