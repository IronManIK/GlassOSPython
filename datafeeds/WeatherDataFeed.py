from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from pyowm.weatherapi25.uris import DAILY_FORECAST_URI

def getWeather():
    #Open weather map setup
    owm = OWM('5749f333920e0129251d1758df0a622a')
    mgr = owm.weather_manager()
    observation = mgr.weather_at_coords(42.291970, -83.535480) #setting it to my house
    w = observation.weather

    #geting data
    return w.temperature('fahrenheit')