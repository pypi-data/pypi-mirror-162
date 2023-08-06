import random
from Shynatime import ShTime
from ShynaProcess import ShynaGreetings


class BroadcastMessageDecision:
    """
    broadcast_morning_decision: return greetings message ready to forward or just greet.
    """
    s_time = ShTime.ClassTime()
    s_greet = ShynaGreetings.ShynaGreetings()
    msg_send = "Today is not the day"
    choose_day = []

    def broadcast_morning_decision(self):
        try:
            today_day = int(self.s_time.get_day_of_week())
            divide_unit = random.choice([0, 1, 2, 3, 4, 5, 6])
            for i in range(0, int(divide_unit)):
                self.choose_day.append(i)
            if today_day in self.choose_day:
                self.msg_send = self.s_greet.greet_good_morning()
            else:
                self.msg_send = "Good Morning, Shiv!"
        except Exception as e:
            self.msg_send = "Today is not the day"
            print(e)
        finally:
            return self.msg_send

    def broadcast_night_decision(self):
        try:
            today_day = int(self.s_time.get_day_of_week())
            divide_unit = random.choice([0, 1, 2, 3, 4, 5, 6])
            for i in range(0, int(divide_unit)):
                self.choose_day.append(i)
            if today_day in self.choose_day:
                self.msg_send = self.s_greet.greet_good_night()
            else:
                self.msg_send = "Good Night, Shiv!"
        except Exception as e:
            self.msg_send = "Today is not the day"
            print(e)
        finally:
            return self.msg_send

