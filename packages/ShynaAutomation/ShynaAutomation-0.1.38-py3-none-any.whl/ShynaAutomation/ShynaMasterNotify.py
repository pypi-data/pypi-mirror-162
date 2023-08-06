from ShynaProcess import ShynaBotNotification, ShynaBroadcastMessageDecision, ShynaSpeak
from ShynaDatabase import ShynaIs, Shdatabase
from Shynatime import ShTime
import random

class MasterNotify:
    """Notifying at telegram via bot notification class. creating notification for failed services for now.
    Services are :
    * is_termux_device_online
    * is_cam_online
    * saw_after_long_time
    * broadcast_morning_decision
    * broadcast_night_decision
    For now this is a test phase and if every thing works fine then we may update the service as per the daily routine.
    may need to think further to all services that can be added.
    """
    s_notify = ShynaBotNotification.BotShynaTelegram()
    s_broadcast = ShynaBroadcastMessageDecision.BroadcastMessageDecision()
    s_is = ShynaIs.ShynaIs()
    s_speak = ShynaSpeak.ShynaSpeak()
    s_time = ShTime.ClassTime()
    is_this = {}
    s_notify.message = " Good day"
    s_data = Shdatabase.ShynaDatabase()

    def dict_compare(self, d1, d2):
        d1_keys = set(d1.keys())
        d2_keys = set(d2.keys())
        shared_keys = d1_keys.intersection(d2_keys)
        added = d1_keys - d2_keys
        removed = d2_keys - d1_keys
        modified = {o: (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
        same = set(o for o in shared_keys if d1[o] == d2[o])
        return added, removed, modified, same

    def notify_broadcast(self):
        print("Is it today?")
        try:
            if self.s_time.string_to_time(time_string="5:30:00") < self.s_time.string_to_time(time_string=self.s_time.now_time) < self.s_time.string_to_time(time_string="5:31:00"):
                self.s_notify.message = self.s_broadcast.broadcast_morning_decision()
                self.s_notify.bot_send_broadcast_msg_to_master()
            if self.s_time.string_to_time(time_string="22:30:00") < self.s_time.string_to_time(time_string=self.s_time.now_time) < self.s_time.string_to_time(time_string="22:31:00"):
                self.s_notify.message = self.s_broadcast.broadcast_night_decision()
                self.s_notify.bot_send_broadcast_msg_to_master()
        except Exception as e:
            print(e)
        finally:
            self.s_data.set_date_system(process_name="broadcast_greet")

    def inform_master(self):
        print("Anything Shiv Should know?")
        is_this_local = {}
        self.s_data.query = "Select * from master_notify where status = 'False' order by count DESC limit 1"
        result = self.s_data.select_from_table()
        try:
            self.is_this['cam_back'] = str(self.s_is.saw_after_long_time())
            self.is_this['termux_online'] = str(self.s_is.is_termux_device_online())
            self.is_this['walk'] = str(self.s_is.is_shivam__still_walking_driving())
            if str(result[0]).lower().__contains__('empty'):
                self.s_data.query = "Insert into master_notify (task_date,task_time,cam_back,termux_online,walk) values('"+str(self.s_time.now_date)+"','"+str(self.s_time.now_time)+"','"+str(self.is_this['cam_back'])+"','"+str(self.is_this['termux_online'])+"','"+str(self.is_this['walk'])+"')"
                self.s_data.create_insert_update_or_delete()
            else:
                self.s_data.query = "Update master_notify set status='True' where count='"+str(result[0][0])+"'"
                self.s_data.create_insert_update_or_delete()
                is_this_local['cam_back'] = str(result[0][3])
                is_this_local['termux_online'] = str(result[0][4])
                is_this_local['walk'] = str(result[0][5])
            if self.is_this == is_this_local:
                print("All same")
            else:
                added, removed, modified, same = self.dict_compare(self.is_this, is_this_local)
                name = list(modified.keys())
                if len(name) > 0:
                    self.s_notify.message = "Loading services with error"
                    self.s_notify.bot_send_msg_to_master()
                    if 'walk' in name:
                        if str(result[0][5]).lower().__eq__('false'):
                            pass
                        else:
                            self.s_notify.message = "I sense you are " + str(result[0][5])
                            self.s_notify.bot_send_msg_to_master()
                    if 'termux_online' in name:
                        if str(result[0][4]).lower().__eq__('true'):
                            self.s_notify.message = " Termux services are back online"
                            self.s_notify.bot_send_msg_to_master()
                        else:
                            self.s_notify.message = " Termux services offline"
                            self.s_notify.bot_send_msg_to_master()
                    if 'cam_back' in name:
                        if str(result[0][3]).lower().__eq__('true'):
                            self.s_notify.message = "Welcome back Shiv"
                            self.s_notify.bot_send_msg_to_master()
                        else:
                            pass
                self.s_data.query = "Insert into master_notify (task_date,task_time,cam_back,termux_online,walk) values('" + str(self.s_time.now_date) + "','" + str(self.s_time.now_time) + "','" + str(self.is_this['cam_back']) + "','" + str(self.is_this['termux_online']) + "','" + str(self.is_this['walk']) + "')"
                self.s_data.create_insert_update_or_delete()
        except Exception as e:
            self.s_notify.message = str(e)
            self.s_notify.bot_send_msg_to_master()
        finally:
            self.s_data.set_date_system(process_name="Master_notify")

    def welcome_back_home(self):
        try:
            self.s_data.query = "Select connection_type, count from connection_check order by count DESC limit 2"
            result = self.s_data.select_from_table()
            if str(result[0][0]).lower().__contains__('empty'):
                pass
            else:
                print(result[0][0], result[1][0])
                print(result[0][1], result[1][1])
                if str(result[0][0]).lower().__eq__('home') and str(result[1][0]).lower().__eq__('phone'):
                    self.s_notify.message = random.choice(["Welcome back home,Shiv!", "Finally you are home, how was it is outside?"])
                    self.s_notify.bot_send_broadcast_msg_to_master()
                    self.s_data.query = "Insert into termux_speak (sent_speak, task_time, task_date) VALUES('" + str(self.s_notify.message) + "', '" + str(self.s_time.now_time) + "', '" + str(self.s_time.now_date) + "')"
                    self.s_data.create_insert_update_or_delete()
                elif str(result[0][0]).lower().__eq__('phone') and str(result[1][0]).lower().__eq__('home'):
                    self.s_notify.message = random.choice(["So we are going out, great!", "Yeah, take me for ride", "So this is how fresh oxygen smell like, it is funny right?"])
                    self.s_notify.bot_send_broadcast_msg_to_master()
                    self.s_data.query = "Insert into termux_speak (sent_speak, task_time, task_date) VALUES('"+str(self.s_notify.message)+"', '"+str(self.s_time.now_time)+"', '"+str(self.s_time.now_date)+"')"
                    self.s_data.create_insert_update_or_delete()
                else:
                    pass
                self.s_data.query = "Update connection_check set status='True' where count='"+str(result[1][1])+"'"
                self.s_data.create_insert_update_or_delete()
        except Exception as e:
            print(e)
        finally:
            self.s_data.set_date_system(process_name="welcome_back_home")

    # def get_news_as_per_automation(self):
    #     try:
    #         self.s_data.query = "Select news_keyword from news_keyword where repeat_count > 9"
    #         result = self.s_data.select_from_table()
    #         for item in result:
    #             self.s_data.query = "Select news_title, "
    #     except Exception as e:
    #         print(e)


if __name__ == '__main__':
    MasterNotify().inform_master()
    MasterNotify().notify_broadcast()
    MasterNotify().welcome_back_home()

#
# test = MasterNotify()
# test.get_news_as_per_automation()