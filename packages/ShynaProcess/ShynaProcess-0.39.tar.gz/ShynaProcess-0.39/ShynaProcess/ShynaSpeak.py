from ShynaDatabase import Shdatabase
from Shynatime import ShTime
from nltk import sent_tokenize
from google_speech import Speech
import random
import os


# TODO: database used, Need to update the table and database setting

class ShynaSpeak:
    """
    Using google_speech library https://pypi.org/project/google-speech/ and nltk to tokenize every sentence and speak.
    make sure the dependencies for google_speech is installed before using this class.
    sox effect are in place, keep Shyna voice same across the devices.

    There are two methods:
     shyna_speaks: provide sentence(s) to speak out loud
     test_shyna_speaks: run to test everything working fine

    """
    lang = "en"
    sox_effects = ("speed", "1.0999",)
    text = "Hey! Shiv? I hope you can listen to me otherwise doesn't matter what I say or do, you will be only " \
           "complaining"
    s_data = Shdatabase.ShynaDatabase()
    s_time = ShTime.ClassTime()

    def shyna_speaks(self, msg):
        try:
            for i in sent_tokenize(msg):
                speech = Speech(i, self.lang)
                speech.play(self.sox_effects)
        except Exception as e:
            print(e)

    def test_shyna_speaks(self):
        self.shyna_speaks(self.text)

    def shyna_speaks_termux(self, msg):
        """
        Speak function with toast notification.
        In those cases when Shyna is set to sleep the function take care of this itself to speaker to just create a notification.
        Dependency :
        1) speak_or_not()
        2) Updated for Android device Only.
        """
        try:
            msgs = random.choice(str(msg).split("|"))
            if str(self.speak_or_not()).lower().__eq__('awake'):
                for i in sent_tokenize(msgs):
                    speech = Speech(i, self.lang)
                    speech.play(self.sox_effects)
            else:
                command = "termux-notification -t " + msgs
                os.popen(cmd=command)
        except Exception as e:
            command = "termux-toast I prefer to stay silent"
            os.popen(cmd=command)
            print(e)

    def speak_or_not(self):
        #  Flow 5. it checks what is the last status I send her. it is morning, silent, or sleep and return accordingly. Default is set to awake.
        result = "awake"
        try:
            self.s_data.query = "SELECT greet_string FROM greeting order by count DESC limit 1;"
            cursor = self.s_data.select_from_table()
            if str(cursor).__contains__('Exception') or str(cursor).__contains__('Empty'):
                pass
            else:
                for row in cursor:
                    greet_string = str(row[0])
                    if len(greet_string) > 0:
                        if str(greet_string).lower() == 'morning':
                            result = 'awake'
                        if str(greet_string).lower() == 'silent':
                            result = 'silent'
                        if str(greet_string).lower() == 'sleep':
                            result = 'sleep'
                    else:
                        result = 'awake'
        except Exception as e:
            print(e)
            result = "awake"
        finally:
            return result

    # Todo: the response can be improved: May be an automation to say the string from the last greet message

    def updated_speak_or_not_status(self, status):
        try:
            if status is False:
                self.s_data.query = "INSERT INTO greeting (new_date, new_time, greet_string) VALUES ('" \
                                    + str(self.s_time.now_date) + "', '" + str(self.s_time.now_time) + "', 'sleep')"
                self.s_data.create_insert_update_or_delete()
                self.shyna_speaks_termux(msg="Okay! I will not disturb anymore")
            else:
                self.s_data.query = "INSERT INTO greeting (new_date, new_time, greet_string) VALUES ('" \
                                    + str(self.s_time.now_date) + "', '" + str(self.s_time.now_time) + "', 'awake')"
                self.s_data.create_insert_update_or_delete()
                self.shyna_speaks_termux(msg="Hey! How are you doing?")
        except Exception as e:
            print(e)
            self.shyna_speaks_termux(msg="Sorry, what was that?")
