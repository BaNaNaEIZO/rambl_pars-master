import json
import datetime
import os
import re
import string
from nltk import word_tokenize, Text
import requests
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import string

days = 100
pages = 50

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60"}
current_time = datetime.datetime.today() - datetime.timedelta(1)
date_list = [current_time - datetime.timedelta(days=x) for x in range(days)]  # Создание списка дней


def get_tags_from_json():
    with open("tags_old.json", mode="r", encoding="utf-8") as r_file:
        data = r_file.read()
        data = json.loads(data)

    return data


def get_date_request():
    for current_time_req in date_list:
        for current_page_req in range(1, pages + 1):
            url = f"https://peroxide.rambler.ru/v1/projects/1/clusters/?limit=50&page={current_page_req}&date={current_time_req.year}-{current_time_req.month}-{current_time_req.day}"
            yield url


def page_request(tags):
    tag_list = []
    tag_value_list = []
    new_list = []
    new_list2 = []

    for key in tags.keys():
        tag_list.append(key)
    for key in tags.values():
        tag_value_list.append(key)
    # print(tag_value_list)

    for str_to_list in tag_value_list:
        for new_values in re.split(r', ', str_to_list):
            new_list.append(new_values)
        new_list = list(set(new_list))
        new_list2.append(new_list)
        new_list = []

    for url in get_date_request():
        try:
            data_json = requests.get(url, headers)
            data = json.loads(data_json.text)
        except ValueError:
            print("//Обработана ошибка запроса//\n",
                  "\nПродолжается выполнение программы...")
        if len(data) != 0:
            temp_list = []
            for i in range(len(data)):
                try:
                    value_annotation = data[i]["long_title"]
                except KeyError:
                    print("Страница ", data)
                    print("Индекс ", i)
                    print(len(data))
                count = -1
                for values in new_list2:
                    count += 1
                    try:
                        for my_str in re.split(r'[ ,«»":()]+', value_annotation):
                            for value in values:
                                # print(re.split(r',', values))
                                if my_str.lower() == value.strip():
                                    with open(f"files/{tag_list[count]}.txt", mode="a") as f:
                                        try:
                                            f.write(my_str.lower() + "\t" + value_annotation + "\n")
                                        except UnicodeEncodeError:
                                            print(value_annotation + "\t" + my_str.lower() + "\t" + tag_list[count] + "\t")
                    except TypeError:
                        print("Какая то ошибка")


def work_with_text(tags):
    tag_list = []
    smd = {}
    for key in tags.keys():
        tag_list.append(key)
    for tag in tag_list:
        if os.path.exists(f"files/{tag}.txt"):
            with open(f"files/{tag}.txt", mode="r") as r:
                text = r.read()
                text = text.lower()
                spec_chars = string.punctuation + string.digits + "«»–"  # + string.ascii_letters
                text = "".join([ch for ch in text if ch not in spec_chars])
                text_tokens = word_tokenize(text)
                text = Text(text_tokens)
                fdist = FreqDist(text)
                russian_stopwords = stopwords.words("russian")
                russian_stopwords.append("\"")
                # print(fdist.most_common(10))
                filtered_words = [word for word in fdist if word not in russian_stopwords]
                weight = 1.0
                list_filter_word = []
                for filterw in filtered_words[1:50]:
                    list_filter_word.append([f"{filterw}", weight])
                    weight -= 0.01

                smd[tag] = list_filter_word
        else:
            print(tag, "Не существует")

    json_object = json.dumps(smd, indent=4, ensure_ascii=False)
    # print(json_object)

    with open(f"all_tags.json", mode="w", encoding="utf-8") as f:
        f.write(json_object)


def main():
    tags = get_tags_from_json()
    page_request(tags)
    work_with_text(tags)


if __name__ == '__main__':
    main()
