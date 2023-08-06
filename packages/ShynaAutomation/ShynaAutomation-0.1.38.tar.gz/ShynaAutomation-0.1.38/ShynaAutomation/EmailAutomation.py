from imbox import Imbox
from Shynatime import ShTime
from ShynaDatabase import Shdatabase
import os
import re
from bs4 import BeautifulSoup
import datetime
import mysql.connector


class ShynaEmailAutomation:
    s_data = Shdatabase.ShynaDatabase()
    s_time = ShTime.ClassTime()
    database_user = 'pythoqdx_Shyna'
    default_database = 'pythoqdx_Shyna'
    host = os.environ.get('host')
    passwd = os.environ.get('passwd')
    device_id = os.environ.get('device_id')
    email_hostname = "imap.gmail.com"
    email_master_address = os.environ.get('imbox_username')
    pass_master_address = os.environ.get('imbox_password')
    result = ""

    def get_regex(self, cut_string):
        print("entering get regex")
        regex = r"(.(r).(n))"
        test_str = cut_string
        subst = ''
        self.result = re.sub(regex, subst, test_str, 0, re.MULTILINE)
        if self.result:
            final = str(str(self.result).split('Dear Customer,')[-1]).split('\n \n Warm')
            if str(final[0]).__contains__('credited to A/c'):
                final_stmt = str(final[0]).split('credited to A/c')[0]
                return "+" + final_stmt.strip('\n \n')
            elif str(final[0]).__contains__('debited from account'):
                final_stmt = str(final[0]).split('debited from account')[0]
                return "-" + final_stmt.strip('\n \n')
        else:
            return False

    def insert_in_transition_table(self, amount, amount_type, date, uid):
        mydb = mysql.connector.connect(
            host=self.host,
            user=self.database_user,
            passwd=self.passwd,
            database=self.default_database
        )
        try:
            print("Entering insert_in_transition_table")
            mycursor = mydb.cursor()
            mycursor.execute("INSERT INTO transition_table(amount_type,amount,now_time, email_date, uid) VALUES (%s, %s, %s, %s, %s)", (str(amount_type), str(amount), str(self.s_time.now_time), str(self.s_time.now_date), str(uid)))
            mydb.commit()
        except Exception as e:
            print("Exception at insert in transition table", e)
        finally:
            mydb.close()

    def add_credit_debit_log(self, uid):
        print("Entering add credit and debit log")
        uid = str(uid).strip('b').strip("'")
        try:
            with Imbox(self.email_hostname, username=self.email_master_address, password=self.pass_master_address,
                       ssl=True, ssl_context=None, starttls=False) as imbox:
                all_inbox_messages = imbox.messages(uid__range=uid)
                for uid, message in all_inbox_messages:
                    soup = BeautifulSoup(str(message.body['html']), features='lxml')
                    statement = self.get_regex(str(soup.get_text('\n')))
                    print(statement)
                    if str(statement).__contains__('+'):
                        amount = self.get_statement_meaning(statement)
                        amount_type = 'credit'
                    elif str(statement).__contains__('-'):
                        amount = self.get_statement_meaning(statement)
                        amount_type = 'debit'
                    print(amount, amount_type)
                    self.insert_in_transition_table(amount=amount, amount_type=amount_type, date=message.date,
                                                    uid=str(uid))
        except Exception as e:
            print("Add credit log Exception", e)

    def get_statement_meaning(self, statement):
        print("getting statement meaning ")
        try:
            regex = r"(\D)"
            test_str = statement
            subst = ''
            self.result = re.sub(regex, subst, test_str, 0, re.MULTILINE)
            if self.result:
                result = int(self.result) / 100
                return str(result)
        except Exception as e:
            print("get statement meaning expection", e)
            pass
        finally:
            print("finally from get statement meaning")

    def get_email_details_by_date(self, date_yr, date_mn, date_day):
        try:
            print("Entering get_email_details_by_date")
            with Imbox(self.email_hostname, username=self.email_master_address, password=self.pass_master_address,
                       ssl=True, ssl_context=None, starttls=False) as imbox:
                all_inbox_messages = imbox.messages(date__gt=datetime.date(date_yr, date_mn, date_day))
                for uid, message in all_inbox_messages:
                    for item in message.sent_from:
                        if str(item['email']).__eq__('alerts@hdfcbank.net'):
                            self.add_credit_debit_log(uid=uid)
                        # print(message.date, "\n", message.subject, "\n", item['email'], "\n", uid)
                        imbox.mark_seen(uid)
                        self.insert_email_database(email_date=str(message.date), email_subject=str(message.subject),
                                                   email_sent_from=str(item['email']), email_uid=str(uid))
        except Exception as e:
            print(e)
            pass
        finally:
            self.check_unread_email()

    def insert_email_database(self, email_date, email_subject, email_sent_from, email_uid):
        try:
            email_date = self.s_time.get_date_and_time(text_string=email_date)
            print("Entering insert_email_database")
            mydb = mysql.connector.connect(
                host=self.host,
                user=self.database_user,
                passwd=self.passwd,
                database=self.default_database
            )
            mycursor = mydb.cursor()
            mycursor.execute("INSERT INTO emaildetails (task_date, task_time, email_date, email_time, email_subject, email_sent_from, email_uid)  VALUES (%s, %s, %s, %s, %s, %s, %s )", (str(self.s_time.now_date), str(self.s_time.now_time), str(email_date[0]), str(email_date[1]), str(email_subject), str(email_sent_from), str(email_uid)))
            mydb.commit()
            if mydb.commit() is None:
                mycursor.execute("Select emailcount from sendercount where senderemail = (%s)", (str(email_sent_from),))
                cursor = mycursor.fetchall()
                # print("This is cursor", cursor, type(cursor), len(cursor), type(len(cursor)))
                for row in cursor:
                    count = row[0]
                    print("count =", row[0])
                if 1 <= len(cursor):
                    count = int(count) + 1
                    # print("inside count =", count)
                    mycursor.execute("UPDATE sendercount SET emailcount = (%s) WHERE senderemail=(%s)",
                                     (str(count), str(email_sent_from)))
                    mydb.commit()
                else:
                    count = 1
                    # print("else", count)
                    mycursor.execute("INSERT INTO sendercount(senderemail,emailcount) VALUES (%s, %s )",
                                     (str(email_sent_from), str(count)))
                    mydb.commit()
        except Exception as e:
            print(e)
        finally:
            self.s_data.set_date_system(process_name="email_details")

    def check_unread_email(self):
        print("Entering check_unread_email")
        try:
            with Imbox(self.email_hostname, username=self.email_master_address, password=self.pass_master_address,
                       ssl=True, ssl_context=None, starttls=False) as imbox:
                all_inbox_messages = imbox.messages(unread=True)
                for uid, message in all_inbox_messages:
                    for item in message.sent_from:
                        print(message.date, "\n", message.subject, "\n", item['email'], "\n", uid)
                        if str(item['email']).__eq__('alerts@hdfcbank.net'):
                            self.add_credit_debit_log(uid=uid)
                        imbox.mark_seen(uid)
                        self.insert_email_database(email_date=str(message.date), email_subject=str(message.subject),
                                                   email_sent_from=str(item['email']), email_uid=str(uid))
        except Exception as e:
            print(e)
        finally:
            self.s_data.set_date_system(process_name="email_details")

    def get_date_system(self):
        print("Entering get_date_system")
        res = "1993-02-02"
        try:
            self.s_data.query = "Select task_date FROM last_run_check WHERE process_name='email_details'"
            cursor = self.s_data.select_from_table()
            if len(cursor) > 0:
                for row in cursor[0]:
                    res = row
                year_default, month_default, date_default = str(res).split('-')
                if int(date_default) > 1:
                    date_default = int(date_default) - 1
                self.get_email_details_by_date(date_day=int(date_default), date_mn=int(month_default), date_yr=int(year_default))
            else:
                year_default, month_default, date_default = str(res).split('-')
                if int(date_default) > 1:
                    date_default = int(date_default) - 1
                self.get_email_details_by_date(date_day=int(date_default), date_mn=int(month_default),
                                               date_yr=int(year_default))
        except Exception as e:
            print(e)
        finally:
            print("db free from last_run_email_check")


if __name__ == "__main__":
    ShynaEmailAutomation().get_date_system()
