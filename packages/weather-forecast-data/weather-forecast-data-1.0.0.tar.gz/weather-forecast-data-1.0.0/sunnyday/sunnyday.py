import requests, pprint


class Weather:
	"""
	Creates a weather object getting an api key as input
	and either a city name or lat and lon coordinates.

	Package use example:

	# Create a weather object using city name:
	# The api key below is not guaranteed to work.
	# Get your own api key from https://openweathermap.org
	# And wait a couple of hours for api key to be activated.

	# Using the city name:
	>>> weather1 = Weather(apikey="YOUR_API_KEY", city="London")

	#Using latitude and longtitude coordinates:
	>>> weather2 = Weather(apikey="YOUR_API_KEY", lat=51.5073509, lon=-0.1277583)

	# Get complete weather data for the next 12 hours:
	>>> weather1.next_12h()

	# Get simplified weather data for next 12 hours:
	>>> weather2.next_12h_simplified()
	"""
	def __init__(self, apikey, city, lat=None, lon=None):
		if city:
			url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={apikey}&units=metric"
			r = requests.get(url)
			self.data = r.json()
		elif lat and lon:
			url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={apikey}&units=metric"
			r = requests.get(url)
			self.data = r.json()
		else:
			raise TypeError("Provide Either A City Or Lat And Lon Arguments")

		if self.data['cod'] != '200':
			raise ValueError("Invalid City")

	def next_12h(self):
		"""
		Return 3 hours data for next 12 hours as dict.
		"""
		return self.data["list"][:4]

	def next_12h_simplified(self):
		"""
		Returns date, temperature and sky condition every 3 hours for next 12 hours as a tuple of tuples.
		"""
		simple_data = []
		for dicty in self.data['list'][:4]:
			simple_data.append((dicty['dt_txt'], dicty['main']['temp'], dicty['weather'][0]['description']))
		return simple_data