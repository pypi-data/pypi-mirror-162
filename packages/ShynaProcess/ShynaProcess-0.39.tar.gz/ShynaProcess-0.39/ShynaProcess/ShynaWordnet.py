import requests
from nltk.corpus import wordnet
import nltk


class ShynaWordnet:
    """
    Get details of any word. Using NLTK and an API data to get the meaning for now.
    Define the word and run the below methods accordingly.

    """
    word = ""
    result = False
    results_def = []
    results_exam = []
    results_syn = []
    results_ant = []

    def get_examples_from_nltk(self):
        try:
            word_set = wordnet.synsets(self.word)
            if len(word_set) > 0:
                self.result = []
                for item in word_set:
                    self.result.append(item.examples())
            else:
                self.result = False
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def get_meaning_from_nltk(self):
        try:
            word_set = wordnet.synsets(self.word)
            if len(word_set) > 0:
                self.result = []
                for item in word_set:
                    self.result.append(item.definition())
            else:
                self.result = False
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def get_synonyms_from_nltk(self):
        try:
            for syn in wordnet.synsets(self.word):
                if len(str(syn)) > 0:
                    self.result = []
                    for lm in syn.lemmas():
                        self.result.append(lm.name())
                else:
                    self.result = False
        except Exception as e:
            print("Exception", e)
            self.result = False
        finally:
            return self.result

    def get_antonyms_from_nltk(self):
        try:
            for syn in wordnet.synsets(self.word):
                for lm in syn.lemmas():
                    if lm.antonyms():
                        self.result = []
                        self.result.append(lm.antonyms()[0].name())
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def get_antonyms_from_api(self):
        try:
            url_q = "https://api.dictionaryapi.dev/api/v2/entries/en/" + self.word
            response = requests.request("GET", url=url_q)
            if response.status_code == 200:
                results = {}
                self.result = {}
                response = response.json()
                response = response[0]
                for key, value in response.items():
                    results[key] = value
                for item in results['meanings'][0]['definitions']:
                    for key, value in item.items():
                        if key == "antonyms":
                            if len(value) > 0:
                                self.results_ant.append(value)
                self.result['antonyms'] = self.results_ant
            else:
                print(response.json()['message'])
                self.result = False
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def get_synonyms_from_api(self):
        try:
            url_q = "https://api.dictionaryapi.dev/api/v2/entries/en/" + self.word
            response = requests.request("GET", url=url_q)
            if response.status_code == 200:
                results = {}
                self.result = {}
                response = response.json()
                response = response[0]
                for key, value in response.items():
                    results[key] = value
                for item in results['meanings'][0]['definitions']:
                    for key, value in item.items():
                        if key == "synonyms":
                            if len(value) > 0:
                                self.results_syn.append(value)
                self.result['synonyms'] = self.results_syn
            else:
                print(response.json()['message'])
                self.result = False
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def get_meaning_from_api(self):
        try:
            url_q = "https://api.dictionaryapi.dev/api/v2/entries/en/" + self.word
            results_def = []
            response = requests.request("GET", url=url_q)
            if response.status_code == 200:
                results = {}
                self.result = {}
                response = response.json()
                response = response[0]
                for key, value in response.items():
                    results[key] = value
                for item in results['meanings'][0]['definitions']:
                    for key, value in item.items():
                        if key == "definition":
                            results_def.append(value)
                self.result['definition'] = results_def
            else:
                print(response.json()['message'])
                self.result = False
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def get_examples_from_api(self):
        try:
            url_q = "https://api.dictionaryapi.dev/api/v2/entries/en/" + self.word
            response = requests.request("GET", url=url_q)
            if response.status_code == 200:
                results = {}
                self.result = {}
                response = response.json()
                response = response[0]
                for key, value in response.items():
                    results[key] = value
                for item in results['meanings'][0]['definitions']:
                    for key, value in item.items():
                        if key == "example":
                            self.results_exam.append(value)
                self.result['example'] = self.results_exam
            else:
                print(response.json()['message'])
                self.result = False
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def get_antonyms(self):
        try:
            result_nltk = self.get_antonyms_from_nltk()
            result_api = self.get_antonyms_from_api()
            if result_api is False and result_api is False:
                self.result = False
            elif result_api is False and len(str(result_nltk)) > 0:
                self.result = []
                for _ in result_nltk:
                    self.result.append(_)
            elif result_nltk is False and len(str(result_api)) > 0:
                self.result = []
                for _ in result_api['antonyms']:
                    for item in _:
                        self.result.append(item)
            else:
                self.result = []
                for _ in result_api['antonyms']:
                    for item in _:
                        self.result.append(item)
                for _ in result_nltk:
                    self.result.append(_)
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def get_synonyms(self):
        try:
            result_nltk = self.get_synonyms_from_nltk()
            result_api = self.get_synonyms_from_api()
            if result_api is False and result_api is False:
                self.result = False
            elif result_api is False and len(str(result_nltk)) > 0:
                self.result = []
                for _ in result_nltk:
                    self.result.append(_)
            elif result_nltk is False and len(str(result_api)) > 0:
                self.result = []
                for _ in result_api['synonyms']:
                    for item in _:
                        self.result.append(item)
            else:
                self.result = []
                for _ in result_api['synonyms']:
                    for item in _:
                        self.result.append(item)
                for _ in result_nltk:
                    self.result.append(_)
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def get_meaning(self):
        try:
            result_nltk = self.get_meaning_from_nltk()
            result_api = self.get_meaning_from_api()
            if result_api is False and result_api is False:
                self.result = False
            elif result_api is False and len(str(result_nltk)) > 0:
                self.result = []
                for _ in result_nltk:
                    if _:
                        self.result.append(_)
            elif result_nltk is False and len(str(result_api)) > 0:
                self.result = []
                for _ in result_api['definition']:
                    if _:
                        self.result.append(_)
            else:
                self.result = []
                for _ in result_api['definition']:
                    if _:
                        self.result.append(_)
                for _ in result_nltk:
                    if _:
                        self.result.append(_)
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def get_examples(self):
        try:
            result_nltk = self.get_examples_from_nltk()
            result_api = self.get_examples_from_api()
            # print(result_nltk, "\n", result_api)
            if result_api is False and result_api is False:
                self.result = False
            elif result_api is False and len(str(result_nltk)) > 0:
                self.result = []
                for _ in result_nltk:
                    for item in _:
                        if item:
                            self.result.append(item)
            elif result_nltk is False and len(str(result_api)) > 0:
                self.result = []
                for _ in result_api['example']:
                    if _:
                        self.result.append(_)
            else:
                self.result = []
                for _ in result_api['example']:
                    if _:
                        self.result.append(_)
                for _ in result_nltk:
                    for item in _:
                        if item:
                            self.result.append(item)
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result

    def is_word_noun_(self, word):
        try:
            ans = nltk.pos_tag(tokens=list(word))
            val = ans[0][1]
            if val == 'NN' or val == 'NNS' or val == 'NNP':
                self.result = True
            else:
                self.result = False
        except Exception as e:
            print(e)
            self.result = False
        finally:
            return self.result


