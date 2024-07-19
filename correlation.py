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

    def correlation(self):
        list_current_week = []
        sums = []
        row_sum = []
        with pd.ExcelWriter(self.output, engine='xlsxwriter') as writer:
            df, list_of_week, list_of_tag = self.dataframe_transform_to_correlation()
            len_lag = len(list_of_week) - self.k + 1
            for i in range(len_lag):
                df_corr = df.iloc[i:self.k + i, :]

                for item in df_corr.index:
                    list_current_week.append(item)
                df_corr = df_corr.corr()
                self.sum_dataframe(df_corr)
                sums.append(self.sum_dataframe(df_corr))
                row_sum.append("week" + str(list_current_week))
                df_sum = pd.DataFrame(sums, index=row_sum, columns=["positive", "negative", "abs"])
                list_of_all_sums_pos, list_of_all_sums_neg = self.sum_corr(df_corr)
                df_corr.loc[" "] = np.NAN
                df_corr.loc["Положительные"] = list_of_all_sums_pos
                df_corr.loc["Отрицательные"] = list_of_all_sums_neg
                print(df_corr)
                df_corr.to_excel(writer, sheet_name=f'week{list_current_week[0]}-{list_current_week[-1]}',
                                 index=True)

                list_current_week = []
            df_sum.to_excel(writer, sheet_name=f'Итоговый график')


    def sum_corr(self, df):
        list_of_all_sums_pos = []
        list_of_all_sums_neg = []
        for item in df.columns:
            sum_pos = -1
            sum_neg = 0
            list_df = df[item].tolist()
            for i in list_df:
                if i >= 0:
                    sum_pos += i
                else:
                    sum_neg += i
            list_of_all_sums_pos.append(sum_pos)
            list_of_all_sums_neg.append(sum_neg)
        return list_of_all_sums_pos, list_of_all_sums_neg

    def all_news_to_excel(self):
        df = pd.read_csv("files/news.csv")
        sps_weeks = list(set(df.week.tolist()))
        sps_tag_len = len(list(set(df.tag.tolist())))
        sps_tags = df.tag.tolist()[:sps_tag_len]
        sps_sum_news = df.sum_news.tolist()
        sps_weeks.sort(reverse=True)

        list_news = []
        count_of_news_start = 0
        count_of_news_end = len(sps_tags)
        for week in sps_weeks:
            temp_dict = {}
            temp_list = sps_sum_news[count_of_news_start:count_of_news_end]
            i = 0
            for tag in sps_tags:
                temp_dict[tag] = temp_list[i]
                i += 1
            list_news.append(temp_dict)

            count_of_news_end += len(sps_tags)
            count_of_news_start += len(sps_tags)
        column = sps_weeks.copy()
        column.sort()
        df = pd.DataFrame(list_news, index=sps_weeks).T
        df = df.reindex(column, axis="columns")
        df.to_excel("files/all_news.xlsx")

    def all_dependency_news_to_excel(self):
        df = pd.read_csv("files/news.csv")
        sps_weeks = list(set(df.week.tolist()))
        sps_tag_len = len(list(set(df.tag.tolist())))
        sps_tags = df.tag.tolist()[:sps_tag_len]
        sps_sum_news = df.sum_news.tolist()
        sps_weeks.sort(reverse=True)

        count_of_news_start = 0
        count_of_news_end = len(sps_tags)
        with pd.ExcelWriter("files/all_dependency_news.xlsx") as writer:
            for week in sps_weeks:
                list_news = []
                temp_dict_percent = {}
                temp_dict_abs = {}
                temp_list = sps_sum_news[count_of_news_start:count_of_news_end]
                i = 0
                for tag in sps_tags:
                    temp_dict_percent[tag] = round(temp_list[i] / max(temp_list) * 100, 1)
                    temp_dict_abs[tag] = temp_list[i]
                    i += 1
                list_news.append(temp_dict_percent)
                list_news.append(temp_dict_abs)
                df = pd.DataFrame(list_news).T
                df.to_excel(writer, sheet_name=f"week_{week}")
                count_of_news_end += len(sps_tags)
                count_of_news_start += len(sps_tags)

    def all_percent_news_to_excel(self):
        df = pd.read_csv("files/news.csv")
        sps_weeks = list(set(df.week.tolist()))
        sps_tag_len = len(list(set(df.tag.tolist())))
        sps_tags = df.tag.tolist()[:sps_tag_len]
        sps_sum_news = df.sum_news.tolist()
        sps_weeks.sort(reverse=True)

        count_of_news_start = 0
        count_of_news_end = len(sps_tags)
        with pd.ExcelWriter("files/all_percent_news.xlsx") as writer:
            for week in sps_weeks:
                list_news = []
                temp_dict_percent = {}
                temp_dict_abs = {}
                temp_list = sps_sum_news[count_of_news_start:count_of_news_end]
                i = 0
                for tag in sps_tags:
                    temp_dict_percent[tag] = round(temp_list[i] / sum(temp_list) * 100, 1)
                    temp_dict_abs[tag] = temp_list[i]
                    i += 1
                list_news.append(temp_dict_percent)
                list_news.append(temp_dict_abs)
                df = pd.DataFrame(list_news).T
                df.to_excel(writer, sheet_name=f"week_{week}")
                count_of_news_end += len(sps_tags)
                count_of_news_start += len(sps_tags)


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