import requests



class Weather:


    """
    Creates a weather object gettign an apikey as input
    and either a city or lat and lon coordinates.

    Package use exemple:

    #Create a weather object using a city name:
    #The units are set by default to metric, you can change it to 'imperial'
    #The api key below is not guaranteed to work.
    #Get your own api key from https://openweathermap.org
    #And wait a couple of hours for the apikey to be activated, if needed

    > weater1 = Weater('95af3459da325dd9465fc25c81d53f8a', city='Madrid')

    #Using latitude and longitude coordinates:
    > weather2 = Weather('95af3459da325dd9465fc25c81d53f8a', lat = 41.1, lon = -4.1)

    #Get complete weather data for the next 12 hours:
    >weather1.next_12h()

    #Simplified data for the next 12 hours:
    >weather1.next_12h_simplified()

    """

    def __init__(self, apikey=None, city=None, lat=None, lon=None, units='metric'):
        if city:
            url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={apikey}&units={units}'
            r = requests.get(url)
            self.data = r.json()

        elif lat and lon:
            url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={apikey}&units={units}'
            r = requests.get(url)
            self.data = r.json()
        else:
            raise TypeError('Provide valid information')

        if self.data['cod'] != '200':
            raise ValueError(self.data['message'])





    def next_12h(self):
        """Returns 3-hour data for the next 12 hours as dict"""
        return self.data['list'][:4]



    def next_12h_simplified(self):
        simple_data = []
        for i in self.data['list'][:4]:
            simple_data.append((i['dt_txt'], str(i['main']['temp']),  i['weather'][0]['description']))
        return simple_data

