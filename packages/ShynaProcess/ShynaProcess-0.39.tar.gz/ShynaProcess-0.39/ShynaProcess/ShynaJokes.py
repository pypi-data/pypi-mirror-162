import json
import requests


class ShynaJokes:
    """
    Use Rapid API- jokes API
    URL: https://rapidapi.com/Sv443/api/jokeapi-v2/
    There is no limitation but there are chances of repetition. stay alert.
    There are below method to use:
    shyna_random_jokes : any random jokes with no filter whatsoever.
    shyna_joke_contains: takes one parameter 'contains_string'. It will return any random jokes with that string
    contained in it.
    shyna_programming_joke : Random jokes based on programming.
    shyna_pun_joke : Random jokes pun intended.
    shyna_spooky_joke: Random jokes on ghosts.
    shyna_christmas_joke: Random Christmas jokes.
     """
    joke = ""
    status = False
    headers = {
        'x-rapidapi-host': "jokeapi-v2.p.rapidapi.com",
        'x-rapidapi-key': "pG7DIQheytmshvuLgNTRSRs3yTogp1f0rDBjsnjIaJXtHxwvdG"
    }

    def shyna_random_jokes(self):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/Any"

        querystring = {"format": "json"}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                for key, value in response.items():
                    if response['type'] == 'twopart':
                        self.joke = response['setup'] + "\n" + response['delivery']
                    else:
                        self.joke = response['joke']
                    self.status = True
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke

    def shyna_joke_contains(self, contains_string):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/Any"

        querystring = {"format": "json", "contains": str(contains_string)}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if not response['error']:
                    for key, value in response.items():
                        if response['type'] == 'twopart':
                            self.joke = response['setup'] + "\n" + response['delivery']
                        else:
                            self.joke = response['joke']
                    self.status = True
                else:
                    self.status = False
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke

    def shyna_programming_joke(self):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/programming"

        querystring = {"format": "json"}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if not response['error']:
                    for key, value in response.items():
                        if response['type'] == 'twopart':
                            self.joke = response['setup'] + "\n" + response['delivery']
                        else:
                            self.joke = response['joke']
                    self.status = True
                else:
                    self.status = False
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke

    def shyna_pun_joke(self):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/pun"

        querystring = {"format": "json"}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if not response['error']:
                    for key, value in response.items():
                        if response['type'] == 'twopart':
                            self.joke = response['setup'] + "\n" + response['delivery']
                        else:
                            self.joke = response['joke']
                    self.status = True
                else:
                    self.status = False
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke

    def shyna_spooky_joke(self):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/spooky"

        querystring = {"format": "json"}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if not response['error']:
                    for key, value in response.items():
                        if response['type'] == 'twopart':
                            self.joke = response['setup'] + "\n" + response['delivery']
                        else:
                            self.joke = response['joke']
                    self.status = True
                else:
                    self.status = False
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke

    def shyna_christmas_joke(self):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/christmas"

        querystring = {"format": "json"}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if not response['error']:
                    for key, value in response.items():
                        if response['type'] == 'twopart':
                            self.joke = response['setup'] + "\n" + response['delivery']
                        else:
                            self.joke = response['joke']
                    self.status = True
                else:
                    self.status = False
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke
