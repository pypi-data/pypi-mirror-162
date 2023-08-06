from imdb import IMDb


class ShynaMovie:
    ia = IMDb()
    movie_details = {}

    def shyna_get_movie_from_name(self, movie_name):
        try:
            movie = self.ia.search_movie(movie_name)
            for i in range(len(movie)):
                self.movie_details[i + 1] = [movie[i].getID(), movie[i]['title']]
            return self.movie_details
        except Exception as e:
            print(e)

    def shyna_get_movie_from_move_id(self, movie_id):
        try:
            movie_info = self.ia.get_movie(movie_id, info=['taglines', 'plot'])
            result = "Tagline: " + str(movie_info.get('taglines')) + "\n\n\n Plot: " + str(movie_info.get('plot'))
            result = str(result).replace("[", '')
            result = str(result).replace("]", '')
            return result
        except Exception as e:
            print(e)

    def shyna_get_movie_taglines(self, movie_id):
        try:
            movie_info = self.ia.get_movie(movie_id, info=['taglines'])
            result = " Tag lines: " + str(movie_info.get('taglines'))
            result = str(result).replace("[", '')
            result = str(result).replace("]", '')
            return result
        except Exception as e:
            print(e)

    def shyna_get_movie_plot(self, movie_id):
        try:
            movie_info = self.ia.get_movie(movie_id, info=['plot'])
            result = " Plot: " + str(movie_info.get('plot'))
            result = str(result).replace("[", '')
            result = str(result).replace("]", '')
            return result
        except Exception as e:
            print(e)
