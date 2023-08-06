from googlesearch import search


class ShynaGoogleSearch:
    """
    perform google search and return the result in form of link.
    define search string as class property.

    Two functions:
    search_google_with_top_result -  Return only one link result
    search_google_with_limit_result - ask for number of result needed and return result in form of link.
    :returns: list
    """
    search_string = ''
    result = []

    def search_google_with_top_result(self):
        for item in search(term=self.search_string, num_results=1):
            self.result.append(item)
        return self.result

    def search_google_with_limit_result(self, result_number):
        for item in search(term=self.search_string, num_results=result_number):
            self.result.append(item)
        return self.result

