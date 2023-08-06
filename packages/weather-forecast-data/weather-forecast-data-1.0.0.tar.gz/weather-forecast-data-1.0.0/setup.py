from setuptools import setup

setup(
	name='weather-forecast-data',
	version='1.0.0',
	packages=['sunnyday'],
	url='https://github.com/Van-Giang-Pro/Weather_Forecast.git',
	license='MIT',
	author='Văn Giang',
	author_email='vangiang260694@gmail.com',
	description='Weather Forecast Data',
	install_requires=['requests'],
	keywords=['weather', 'forecast', 'openweather'],
	classifiers=['Development Status :: 3 - Alpha',
	             'Intended Audience :: Developers',
	             'Topic :: Software Development :: Build Tools',
	             'License :: OSI Approved :: MIT License',
	             'Programming Language :: Python :: 3.5',
	             'Programming Language :: Python :: 3.6',
	             'Programming Language :: Python :: 3.7',
	             'Programming Language :: Python :: 3.8']
)
