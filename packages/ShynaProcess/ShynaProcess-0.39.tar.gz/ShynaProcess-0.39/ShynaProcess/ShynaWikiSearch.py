import wikipedia


class ShynaWikiSearch:
    """
    perform wikipedia search.
    define search string as class property.
    Below functions available for use
    search_wiki_page: return the complete page with set search string.
    one_line_introduction: return one line summary of set search string
    set_line_introduction: provide the number of summary sentences needed.
    """
    search_string = ''

    def search_wiki_page(self):
        page_details = wikipedia.page(title=self.search_string, preload=False, auto_suggest=False)
        return page_details.content

    def one_line_introduction(self):
        sentence_summary = wikipedia.summary(title=self.search_string, sentences=1, auto_suggest=False)
        return sentence_summary

    def set_line_introduction(self, num_sent):
        sentence_summary = wikipedia.summary(title=self.search_string, sentences=num_sent, auto_suggest=False)
        return sentence_summary

