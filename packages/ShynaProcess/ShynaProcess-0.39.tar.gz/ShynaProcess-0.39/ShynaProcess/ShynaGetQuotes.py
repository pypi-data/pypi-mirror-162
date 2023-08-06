import time
import nltk
import requests
import random


class GetQuotes:
    """
    We will get quotes form the API I got form Rapid API website link is
    https://rapidapi.com/martin.svoboda/api/quotes15/pricing
    It allows us to request 1 per second, unlimited. we need to get the quotes and analyse them right away
    """
    get_id = {
        'x-rapidapi-host': "quotes15.p.rapidapi.com",
        'x-rapidapi-key': "pG7DIQheytmshvuLgNTRSRs3yTogp1f0rDBjsnjIaJXtHxwvdG"
    }
    key = []
    is_noun = lambda pos: pos[:2] == 'NN'
    content = ''
    tags = []
    originator = []
    status = True

    def extract_noun(self, tag_list):
        nouns = [word for (word, pos) in nltk.pos_tag(tag_list) if self.is_noun]
        return nouns

    def get_quotes(self):
        """This function will get the quotes at wait of 1 seconds and return to quote analyse function"""
        try:
            while self.status is True:
                time.sleep(1)
                url = "https://quotes15.p.rapidapi.com/quotes/random/"
                querystring = {"language_code": "en"}
                headers = self.get_id
                response = requests.request("GET", url, headers=headers, params=querystring)
                response = eval(response.__dict__['_content'].decode('utf-8'))
                for _ in response.items():
                    self.content = response['content']
                    self.tags = response['tags']
                    self.originator = response['originator']
                if "muslim" in self.tags or "religious" in self.tags:
                    self.status = True
                else:
                    self.status = False
            final = self.analysing_quotes(content=self.content, tags=self.tags, originator=self.originator)
            return final
        except Exception as e:
            print(e)

    def analysing_quotes(self, content, tags, originator):
        self.content = content
        self.tags = tags
        self.originator = originator
        try:
            noun = self.extract_noun(tag_list=self.tags)
            noun = random.choice(noun)
            response_is = "I was reading over the Internet about '" + noun + "', " + str(
                originator['name']) + " said once '" + str(content) + "'"
            return response_is
        except Exception as e:
            print(e)
