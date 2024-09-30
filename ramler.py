import numpy as np
import pandas as pd
import requests
import datetime
import json
import csv
import re
import shutil
import os


# Парсер выполняет поиск по ссылке https://peroxide.rambler.ru/v1/projects/1/clusters/?limit=50&page=1&date=2023-12-31
#
# Входные параметры: days, pages, tag_file, output, encoding
# days - Период сбора информации начиная с текущего дня
# page - Количество проверяемых страниц в рамках одного дня (одна страница - 50 новостей. В день выходит около 60 страниц новостей)
# tag_file - Файл с тэгами
# output - Выходной файл с полученной информации с сайта
# encoding - Кодировка выходного файла
#
#
#

class RamblerPars:
    def __init__(self, days=100, pages=1, tag_file="tags.json", output="files/news.csv", encoding="utf-8",
                 start_day=datetime.datetime.today()):
        # Текущая дата
        self.current_time = start_day

        # Если раскоментированно, то выполняет парсинг начиная с 31.12.2023. Важно: Необходимо раскоментировать костыль (строка 15 в correlation.py)
        # current_time = datetime.datetime.today() - datetime.timedelta(datetime.datetime.today().day) # 31.12.2023

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60"}  # Заголовок для парсера
        self.days = days
        self.pages = pages
        self.tag_file = tag_file
        self.output = output
        self.encoding = encoding
        self.tags = self.get_tags_from_json()
        self.date_list = [self.current_time - datetime.timedelta(days=x) for x in range(days)]  # Создание списка дней

    def get_current_time(self):
        return datetime.datetime.today()

    def get_time_work(self):
        current_time = self.current_time
        time_work = self.days * self.pages
        delta_time_work = current_time + datetime.timedelta(minutes=(time_work // 60), seconds=(time_work % 60))
        print("\nНачало работы: "f"{current_time.hour}ч. {current_time.minute}м. {current_time.second}с. "
              f"\nКонец работы: {delta_time_work.hour}ч. {delta_time_work.minute}м. {delta_time_work.second}с.\n")

    # Забираем словарь с тэгами из файла
    def get_tags_from_json(self):
        # self.get_time_work()
        with open(self.tag_file, mode="r", encoding="utf-8") as r_file:
            data = r_file.read()
            data = json.loads(data)
            # for item in data:
            #     tags = data[item].split(", ")
            #     data[item] = tags
        return data

    # Запрос к сайту и запись данных в файл
    def page_request(self):
        with open(self.output, mode="w", encoding=self.encoding) as w_file:
            file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
            file_writer.writerow(["week", "tag", "sum_news"])
            tag_list = []
            df_for_news_str = pd.DataFrame()

            current_week = self.current_time.isocalendar().week
            for key in self.tags.keys():
                tag_list.append(key)

            news_from_week = [x * 0 for x in range(len(tag_list))]

            list_for_news_str = [[] for x in range(len(tag_list))]

            for weeks, url in self.get_date_request():

                try:
                    data_json = requests.get(url, self.headers)
                    data = json.loads(data_json.text)
                except ValueError:
                    print(data_json.text, data_json,
                          "\n//Обработана ошибка запроса//\nПродолжается выполнение программы...")

                if current_week != weeks:
                    i = 0
                    print("Неделя: " + str(current_week) + " " + str(news_from_week))
                    for row in news_from_week:
                        file_writer.writerow([current_week, tag_list[i], row])
                        i += 1
                    df_for_news_str = pd.DataFrame(list_for_news_str, index=tag_list).T
                    with pd.ExcelWriter(f"files/news_from_week/news_from_{current_week}_week.xlsx") as writer:
                        for count in range(len(df_for_news_str.columns)):
                            df_for_news_str[tag_list[count]].to_excel(writer, sheet_name=tag_list[count])

                    current_week = weeks

                    news_from_week = [x * 0 for x in range(len(tag_list))]
                    df_for_news_str = pd.DataFrame()
                    list_for_news_str = [[] for x in range(len(tag_list))]

                if len(data) != 0:
                    temp_list = []

                    for i in range(len(data)):
                        try:
                            value_annotation = data[i]["long_title"]
                            value_id = data[i]["id"]
                            value_normalized_title = data[i]["normalized_title"]
                        except KeyError:
                            print("Страница ", data)
                            print("Индекс ", i)
                            print(len(data))

                        key_and_values_list = []
                        for tag in tag_list:
                            for item in self.tags.get(tag):
                                temp_list.append([tag, item[0], item[1]])
                            key_and_values_list.append(temp_list)
                            temp_list = []
                        var, news = self.search(value_annotation, key_and_values_list)  # 46 TypeError
                        # if var >= 0:
                        #     news_from_week[var] += 1
                        #     list_for_news_str[0][var].append(f"https://news.rambler.ru/{value_id}-{value_normalized_title}")
                        #     list_for_news_str[1][var].append(value_annotation.replace('"', ""))
                        # else:
                        #     list_for_news_str[var].append(value_annotation.replace('"', ""))
                        #     print(value_annotation.replace('"', ""))
                        #     print(my_str)
                        if var >= 0:
                            news_from_week[var] += 1
                            my_str = '=HYPERLINK("{}", "{}")'.format(
                                f"https://news.rambler.ru/{value_id}-{value_normalized_title}",
                                value_annotation.replace('"', ""))
                            if len(f"https://news.rambler.ru/{value_id}-{value_normalized_title}") < 255:
                                list_for_news_str[var].append(my_str)
                            else:
                                list_for_news_str[var].append(value_annotation.replace('"', ""))
                                with open("files/news_from_week/other.txt", mode="a", encoding=self.encoding) as w_txt:
                                    w_txt.write(
                                        f"week_{weeks} tag_{tag_list[var]}  https://news.rambler.ru/{value_id}-{value_normalized_title},  {value_annotation}\n")

    def search(self, in_str, key_and_values_list):
        news_weight_list = [x * 0 for x in range(len(key_and_values_list) + 1)]
        try:
            for my_str in re.split(r'[ ,«»":()]+', in_str):  # 46 TypeError
                count = 1
                for item in key_and_values_list:
                    for value in item:
                        if my_str.lower() == value[1]:
                            news_weight_list[count] += value[2]
                    count += 1
        except TypeError:
            print("//Обработана ошибка поиска//\nПродолжается выполнение программы...")

        return (max(enumerate(news_weight_list), key=lambda x: x[1])[0]) - 1, in_str

    def get_date_request(self):
        for current_time in self.date_list:
            for current_page in range(1, self.pages + 1):
                url = f"https://peroxide.rambler.ru/v1/projects/1/clusters/?limit=50&page={current_page}&date={current_time.year}-{current_time.month}-{current_time.day}"
                # print("ссылка создана")
                yield current_time.isocalendar().week, url


def data_input():
    days = input("Введите days: ")
    pages = input("Введите pages: ")
    weeks = input("Введите weeks: ")
    return days, pages, weeks


def choice_day():
    choice = input("Введите дату или пропустите. Формат(dd/mm/yyyy): ")
    print()
    date = datetime.datetime.today()
    if choice:
        date = datetime.datetime.strptime(choice, '%d/%m/%Y').date()
    return date


def work_with_os():
    if os.path.isdir("files"):
        shutil.rmtree("files")
    if os.path.isdir("files/news_from_week"):
        shutil.rmtree("files/news_from_week")
    os.mkdir("files")
    os.mkdir("files/news_from_week")
