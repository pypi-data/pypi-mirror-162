import requests
from ShynaDatabase import Shdatabase
from Shynatime import ShTime


# TODO: we have database here, need to reconfigure.

class ShynaWeather:
    """
    Define either lon/lat or city_name. for shyna the lat and lon will be fetched from the database.
    get_weather_lon_lat: return weather details in dict as per lat/lon
    get_astronomy_lon_lat: return astro details in dict as per lat/lon
    get_weather_city: return weather details in dict as per city name
    get_astronomy_city : return astro details in dict as per city name
    get_weather: this will return the complete details. astro and weather.
    """

    weather_headers = {
        'x-rapidapi-host': "weatherapi-com.p.rapidapi.com",
        'x-rapidapi-key': "pG7DIQheytmshvuLgNTRSRs3yTogp1f0rDBjsnjIaJXtHxwvdG"
    }
    weather_dict = {}
    astro_dict = {}
    lat = None
    lon = None
    city_name = None
    s_data = Shdatabase.ShynaDatabase()
    s_time = ShTime.ClassTime()

    def get_weather_lon_lat(self):
        url = "https://weatherapi-com.p.rapidapi.com/current.json"
        w_query = str(self.lat) + "," + str(self.lon)
        # querystring = {"q": "28.698255,77.461441"}
        querystring = {"q": w_query}
        try:
            response = requests.request("GET", url=url, headers=self.weather_headers, params=querystring)
            response = eval(response.text)
            for _, val in response.items():
                for key, value in val.items():
                    if key == "condition":
                        self.weather_dict[key] = value['text']
                    else:
                        self.weather_dict[key] = value
        except Exception as e:
            self.weather_dict['error'] = e
            print(e)
        finally:
            return self.weather_dict

    def get_astronomy_lon_lat(self):
        url = "https://weatherapi-com.p.rapidapi.com/astronomy.json"
        w_query = str(self.lat) + "," + str(self.lon)
        querystring = {"q": w_query}
        try:
            response = requests.request("GET", url=url, headers=self.weather_headers, params=querystring)
            response = eval(response.text)
            for _, val in response.items():
                for key, value in val.items():
                    if key == 'astro':
                        for keys, values in value.items():
                            self.astro_dict[keys] = values
                    else:
                        pass
        except Exception as e:
            self.astro_dict['error'] = e
            print(e)
        finally:
            return self.astro_dict

    def get_weather_city(self):
        url = "https://weatherapi-com.p.rapidapi.com/current.json"
        querystring = {"q": self.city_name}
        try:
            response = requests.request("GET", url=url, headers=self.weather_headers, params=querystring)
            response = eval(response.text)
            for _, val in response.items():
                for key, value in val.items():
                    if key == "condition":
                        self.weather_dict[key] = value['text']
                    else:
                        self.weather_dict[key] = value
        except Exception as e:
            self.weather_dict['error'] = e
            print(e)
        finally:
            return self.weather_dict

    def get_astronomy_city(self):
        url = "https://weatherapi-com.p.rapidapi.com/astronomy.json"
        querystring = {"q": self.city_name}
        try:
            response = requests.request("GET", url=url, headers=self.weather_headers, params=querystring)
            response = eval(response.text)
            for _, val in response.items():
                for key, value in val.items():
                    if key == 'astro':
                        for keys, values in value.items():
                            self.astro_dict[keys] = values
                    else:
                        pass
        except Exception as e:
            self.astro_dict['error'] = e
            print(e)
        finally:
            return self.astro_dict

    def get_weather(self):
        try:
            if self.lat is None and self.lon is None and self.city_name is None:
                self.weather_dict['Error'] = "Please define either latitude or Longitude OR city name"
            elif self.lat is None and self.lon is None:
                self.weather_dict = self.get_weather_city()
                self.astro_dict = self.get_astronomy_city()
                self.weather_dict.update(self.astro_dict)
            else:
                self.weather_dict = self.get_weather_lon_lat()
                self.astro_dict = self.get_astronomy_lon_lat()
                self.weather_dict.update(self.astro_dict)
        except Exception as e:
            self.weather_dict['error'] = e
            print(e)
        finally:
            return self.weather_dict

    def get_weather_sentence(self):
        weather_sentence = False
        try:
            self.s_data.query = "SELECT speak_sentence FROM weather_table where task_date = '" \
                                + str(self.s_time.now_date) + "'"
            result = self.s_data.select_from_table()
            for item in result:
                weather_sentence = item[0]
        except Exception as e:
            weather_sentence = False
            print(e)
        finally:
            return weather_sentence
