import pandas as pd
import numpy as np


class Correlation:
    def __init__(self, input_file="files/news.csv", output_file="files/output.xlsx", encoding="utf-8", k=5):
        self.input = input_file
        self.output = output_file
        self.encoding = encoding
        self.k = k

    def load_file(self):
        # Загрузка данных в датафрейм
        df = pd.read_csv(self.input)
        # df = df.drop([i for i in range(len(df["tag"].unique()))])  # Костыль закрыает 53 неделю, которой нет в 2023 году
        return df

    def dataframe_transform_to_correlation(self):
        # Загрузка датафрейма
        df = self.load_file()
        # Параметры стобца week
        list_of_week = [item for item in df["week"].unique()]
        all_week_lenght = len(list_of_week)
        # Параметры столбца tag
        list_of_tag = [item for item in df["tag"].unique()]
        all_tag_lenght = len(list_of_tag)
        # Создаем массив для заполнения нового датафрейма
        data = df["sum_news"].tolist()
        data = np.reshape(data, (all_week_lenght, all_tag_lenght))
        data = np.transpose(data)
        # Создание нового датафрейма на основе старых данных
        df2 = pd.DataFrame(data, columns=list_of_week, index=list_of_tag)
        df2 = df2.transpose()
        return df2, list_of_week, list_of_tag

    def sum_dataframe(self, df):
        sum_positive = 0
        sum_negative = 0
        sum_all = df.abs().sum().sum()
        for i in df.columns:
            for j in df.index:
                value = df.at[i, j]
                if value < 0:
                    sum_negative += value
                elif value > 0:
                    sum_positive += value
        return sum_positive - 45, sum_negative, sum_all - 45

    def correlation(self):
        list_current_week = ""
        sums = []
        row_sum = []
        with pd.ExcelWriter('files/sums.xlsx') as f:
            with pd.ExcelWriter(self.output) as writer:
                df, list_of_week, list_of_tag = self.dataframe_transform_to_correlation()
                len_lag = len(list_of_week) - self.k + 1
                for i in range(len_lag):
                    df_corr = df.iloc[i:self.k + i, :]
                    for item in df_corr.index:
                        list_current_week += "_" + str(item)
                    df_corr = df_corr.corr()
                    df_corr.to_excel(writer, sheet_name=f'week{list_current_week}', index=True)
                    self.sum_dataframe(df_corr)
                    sums.append(self.sum_dataframe(df_corr))
                    row_sum.append("week" + list_current_week)
                    list_current_week = ""
            df_sum = pd.DataFrame(sums, index=row_sum, columns=["positive", "negative", "abs"])
            df_sum.to_excel(f)
