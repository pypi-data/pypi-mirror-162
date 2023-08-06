from Shynatime import ShTime
from ShynaProcess import ShynaNews, ShynaWordnet
from ShynaDatabase import Shdatabase
import mysql.connector
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class ShynaNewsAutomation:
    s_time = ShTime.ClassTime()
    s_news = ShynaNews.ShynaNews()
    s_data = Shdatabase.ShynaDatabase()
    s_word = ShynaWordnet.ShynaWordnet()
    database_user = os.environ.get('user')
    host = os.environ.get('host')
    passwd = os.environ.get('passwd')
    keyword_list = []
    stop_words = set(stopwords.words('english'))
    custom_ignore_keyword_list = ['the', 'how', 'call', 'high', 'says', 'why', 'study', 'full', 'team', 'check',
                                  'women',
                                  'players', 'top', 'may', 'key', 'govt', 'new', 'year', 'list', 'man', 'live', 'yrs']

    def get_news(self):
        try:
            self.s_data.default_database = os.environ.get('status_db')
            self.s_data.query = "Select task_date,task_time from last_run_check where process_name='news_details'"
            last_run_datetime = self.s_data.select_from_table()
            self.s_data.default_database = os.environ.get('news_db')
            self.s_data.query = "SELECT news_urls, host_name, category from news_url"
            result = self.s_data.select_from_table()
            for item in result:
                self.s_news.url = item[0]
                if str(item[1]).lower().__eq__('indiatimes'):
                    print("Getting News from India Times Server from ", item[2], " category")
                    for key, value in self.s_news.get_news_toi().items():
                        if self.s_time.string_to_date(last_run_datetime[0][0]) <= self.s_time.string_to_date(
                                str(value[2])):
                            if self.s_time.string_to_time(last_run_datetime[0][1]) <= self.s_time.string_to_time(
                                    str(value[3])):
                                print(self.s_time.string_to_time(last_run_datetime[0][1]),
                                      self.s_time.string_to_time(str(value[3])))
                                self.insert_news_in_database(news_title=str(key), news_summary=str(value[0]),
                                                             news_link=str(value[1]), news_date=value[2],
                                                             news_time=value[3],
                                                             publish_date_time=str(value[2]) + " " + str(value[3]),
                                                             categories=str(item[2]))
                else:
                    print("Getting News from Zee News Server from ", item[2], " category")
                    for key, value in self.s_news.get_news_zee().items():
                        if self.s_time.string_to_date(last_run_datetime[0][0]) <= self.s_time.string_to_date(
                                str(value[2])) and self.s_time.string_to_time(
                            last_run_datetime[0][1]) <= self.s_time.string_to_time(str(value[3])):
                            # print(self.s_time.string_to_time(last_run_datetime[0][1]),self.s_time.string_to_time(str(value[3])))
                            self.insert_news_in_database(news_title=str(key), news_summary=str(value[0]),
                                                         news_link=str(value[1]), news_date=value[2],
                                                         news_time=value[3],
                                                         publish_date_time=str(value[2]) + " " + str(value[3]),
                                                         categories=str(item[2]))
        except Exception as e:
            print(e)
        finally:
            self.s_data.set_date_system(process_name='get_news')

    def insert_news_in_database(self, news_title, news_summary, news_link, news_date, news_time, publish_date_time,
                                categories):
        mydb = mysql.connector.connect(
            host=self.host,
            user=self.database_user,
            passwd=self.passwd,
            database=str(os.environ.get('news_db'))
        )
        try:
            print("Entering insert_news_in_database")
            my_cursor = mydb.cursor()
            my_cursor.execute("INSERT INTO news_alert (news_title, news_description, news_time, news_date, news_link, "
                              "task_date, task_time, publish_date_time, categories) "
                              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s )", (str(news_title), str(news_summary),
                                                                               str(news_time), str(news_date),
                                                                               str(news_link),
                                                                               str(self.s_time.now_date),
                                                                               str(self.s_time.now_time),
                                                                               str(publish_date_time),
                                                                               str(categories)))
            mydb.commit()
        except Exception as e:
            pass
        finally:
            mydb.close()
            self.s_data.set_date_system(process_name="news_details")

    def update_news_keyword(self):
        print("Updating keyword")
        keyword_list_result = []
        count_list = []
        final_keyword = {}
        keys_list = []
        try:
            self.s_data.default_database = os.environ.get("news_db")
            self.s_data.query = "SELECT news_keyword, repeat_count from news_keyword"
            result = self.s_data.select_from_table()
            if str(result[0]).lower().__eq__('empty'):
                keyword_list_result = ''
            else:
                for item in result:
                    keyword_list_result.append(item)
            print("From Database")
            print(keyword_list_result)
            self.s_data.query = "Select news_title, count from news_alert"
            result = self.s_data.select_from_table()
            if str(result[0]).lower().__eq__('empty'):
                print("No keywords for analysis")
            else:
                for item in result:
                    count_list.append(item[1])
                    word_tokens = word_tokenize(str(item[0]).lower())
                    for keyword in [w for w in word_tokens if not w in self.stop_words]:
                        keyword = "".join(e for e in keyword if e.isalpha())
                        if len(keyword) > 1:
                            self.keyword_list.append(keyword)
                self.keyword_list = {i: self.keyword_list.count(i) for i in self.keyword_list}
                print("Length of key dict", len(self.keyword_list))
                for key, val in self.keyword_list.items():
                    if int(val) < 2 or key in self.custom_ignore_keyword_list or len(
                            str(key)) < 2 or self.s_word.is_word_noun_(str(key)) is False:
                        keys_list.append(key)
                for item in keys_list:
                    del self.keyword_list[item]
                print("From News title")
                print(self.keyword_list)
                for key, value in self.keyword_list.items():
                    if len(keyword_list_result) > 0:
                        for keywords in keyword_list_result:
                            if str(key).__eq__(keywords[0]):
                                # print('same', key)
                                if int(value) < int(keywords[1]):
                                    count = int(keywords[1]) - int(value)
                                    final_keyword[key] = (int(keywords[1]) + int(count))
                                elif int(value) == int(keywords[1]):
                                    pass
                                else:
                                    print("Database have small value", key, value, keywords)
                                    count = int(value) + int(keywords[1])
                                    final_keyword[key] = int(count)
                    else:
                        final_keyword[key] = value
                print("Finally")
                print(final_keyword)
                for key, val in final_keyword.items():
                    self.s_data.query = "INSERT INTO news_keyword (news_keyword,repeat_count,task_date, task_time) " \
                                        "VALUES('" + str(key) + "','" + str(val) + "','" + str(self.s_time.now_date) + \
                                        "','" + str(self.s_time.now_time) + "') ON DUPLICATE KEY UPDATE repeat_count='" \
                                        + str(val) + "', task_date='" + str(self.s_time.now_date) + "', task_time='" \
                                        + str(self.s_time.now_time) + "'"
                    print(self.s_data.query)
                    self.s_data.create_insert_update_or_delete()
                counts = str(count_list).replace('[', '(').replace(']', ')')
                self.s_data.query = "Update news_alert set keyword_process = 'True' where count in " + str(counts)
                self.s_data.create_insert_update_or_delete()
        except Exception as e:
            print(e)
        finally:
            self.s_data.set_date_system(process_name="news_keyword_details")


if __name__ == "__main__":
    ShynaNewsAutomation().get_news()
    ShynaNewsAutomation().update_news_keyword()
