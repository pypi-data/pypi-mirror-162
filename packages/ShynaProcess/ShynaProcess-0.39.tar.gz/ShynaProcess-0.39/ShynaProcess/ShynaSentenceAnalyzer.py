from nltk.corpus import wordnet
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class ShynaSentenceAnalyzer:
    """Using nltk.sentiment.vader
    sentence_analysis : provide sentence to check the polarity. There is nothing like neutral either it is positive or
    negative sentence.
    This will help in case running a command and there is a follow-up question.  Response the way you like as per the
    sentence polarity it will be decided to perform the command or not.

    We have below method:
    sentence_analysis: Provide sentence to this method
    """
    sia = SentimentIntensityAnalyzer()
    pos_score = 0
    neg_score = 0
    neu_score = 0
    comp_score = 0
    antonyms = []
    status = True

    def analyse_sentence_polarity(self, item):
        self.pos_score = self.sia.polarity_scores(text=item)['pos']
        self.neg_score = self.sia.polarity_scores(text=item)['neg']
        self.neu_score = self.sia.polarity_scores(text=item)['neu']
        self.comp_score = self.sia.polarity_scores(text=item)['compound']
        return self.pos_score, self.neg_score, self.neu_score, self.comp_score

    def get_antonyms(self, word_item):
        for syn in wordnet.synsets(word_item):
            for lm in syn.lemmas():
                if lm.antonyms():
                    self.antonyms.append(lm.antonyms()[0].name())
        return self.antonyms

    def is_neutral_sentence_really(self, check_sentence):
        check = []
        words = str(check_sentence).split(" ")
        for word in words:
            any_antonyms = self.get_antonyms(word_item=word)
            if len(any_antonyms) > 0:
                for antonym in any_antonyms:
                    new_sent = str(check_sentence).replace(word, antonym)
                    new_analysis = self.analyse_sentence_polarity(item=new_sent)[3]
                    if new_analysis < 0:
                        check.append(False)
                    else:
                        self.status = True
            else:
                self.status = True
        if False in check:
            self.status = False
        else:
            self.status = True
        return self.status

    def sentence_analysis(self, check_sentence):
        if self.analyse_sentence_polarity(item=check_sentence)[2] == 1.0:
            if self.is_neutral_sentence_really(check_sentence=check_sentence):
                self.status = 'negative'
            else:
                self.status = 'positive'
        else:
            if self.analyse_sentence_polarity(item=check_sentence)[3] < 0:
                self.status = 'negative'
            else:
                self.status = 'positive'
        return self.status



