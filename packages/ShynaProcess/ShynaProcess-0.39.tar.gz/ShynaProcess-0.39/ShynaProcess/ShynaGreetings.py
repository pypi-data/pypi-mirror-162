import json
import requests


class ShynaGreetings:
    """
    I am using a Message API. The messages are filter as per the categories.
    ['Love','quotes','friendship','Good night','Good morning','funny','Birthday','Sad','Sweet','Random']

    API URL: https://rapidapi.com/ajith/api/messages/
    There are no limitation in use, but sometimes it doesn't return a response, in such case False will be returned.

    Below methods available:
    greet_good_morning
    greet_good_night
    greet_friend_ship_day
    greet_birthday
    greet_love
    greet_quotes
    greet_funny
    greet_sweet
    greet_custom: provide from any above category.
    """
    msg = ""
    status = False
    headers = {
        'x-rapidapi-host': "ajith-messages.p.rapidapi.com",
        'x-rapidapi-key': "pG7DIQheytmshvuLgNTRSRs3yTogp1f0rDBjsnjIaJXtHxwvdG"
    }

    def greet_good_morning(self):
        """Send Good morning message suggestion"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'Good morning'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_good_night(self):
        """Send Good night messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'Good night'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_friend_ship_day(self):
        """Send Friend-Ship day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'friendship'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_birthday(self):
        """Send Birthday day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'Birthday'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_love(self):
        """Send Birthday day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'Love'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_quotes(self):
        """Send Birthday day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'quotes'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_funny(self):
        """Send Birthday day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'funny'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_sweet(self):
        """Send Birthday day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'Sweet'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_custom(self, query):
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": query}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg
