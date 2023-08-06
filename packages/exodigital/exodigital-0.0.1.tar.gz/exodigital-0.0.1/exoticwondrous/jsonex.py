from typing import List
from typing import Any
from dataclasses import dataclass

# ExoDigit from exoticwondrous
# Telgram: https//exoticwondrous
# Ahmed Mohammmed
# ahmdsmhmmd@gmail.com   

@dataclass
class AreaName:
    value: str

    @staticmethod
    def from_dict(obj: Any) -> 'AreaName':
        _value = str(obj.get("value"))
        return AreaName(_value)

@dataclass
class Astronomy:
    moon_illumination: str
    moon_phase: str
    moonrise: str
    moonset: str
    sunrise: str
    sunset: str

    @staticmethod
    def from_dict(obj: Any) -> 'Astronomy':
        _moon_illumination = str(obj.get("moon_illumination"))
        _moon_phase = str(obj.get("moon_phase"))
        _moonrise = str(obj.get("moonrise"))
        _moonset = str(obj.get("moonset"))
        _sunrise = str(obj.get("sunrise"))
        _sunset = str(obj.get("sunset"))
        return Astronomy(_moon_illumination, _moon_phase, _moonrise, _moonset, _sunrise, _sunset)

@dataclass
class Country:
    value: str

    @staticmethod
    def from_dict(obj: Any) -> 'Country':
        _value = str(obj.get("value"))
        return Country(_value)

@dataclass
class CurrentCondition:
    FeelsLikeC: str
    FeelsLikeF: str
    cloudcover: str
    humidity: str
    localObsDateTime: str
    observation_time: str
    precipInches: str
    precipMM: str
    pressure: str
    pressureInches: str
    temp_C: str
    temp_F: str
    uvIndex: str
    visibility: str
    visibilityMiles: str
    weatherCode: str
    weatherDesc: List[str]
    weatherIconUrl: List[int]
    winddir16Point: str
    winddirDegree: str
    windspeedKmph: str
    windspeedMiles: str

    @staticmethod
    def from_dict(obj: Any) -> 'CurrentCondition':
        _FeelsLikeC = str(obj.get("FeelsLikeC"))
        _FeelsLikeF = str(obj.get("FeelsLikeF"))
        _cloudcover = str(obj.get("cloudcover"))
        _humidity = str(obj.get("humidity"))
        _localObsDateTime = str(obj.get("localObsDateTime"))
        _observation_time = str(obj.get("observation_time"))
        _precipInches = str(obj.get("precipInches"))
        _precipMM = str(obj.get("precipMM"))
        _pressure = str(obj.get("pressure"))
        _pressureInches = str(obj.get("pressureInches"))
        _temp_C = str(obj.get("temp_C"))
        _temp_F = str(obj.get("temp_F"))
        _uvIndex = str(obj.get("uvIndex"))
        _visibility = str(obj.get("visibility"))
        _visibilityMiles = str(obj.get("visibilityMiles"))
        _weatherCode = str(obj.get("weatherCode"))
        _weatherDesc = [WeatherDesc.from_dict(y) for y in obj.get("weatherDesc")]
        _weatherIconUrl = [WeatherIconUrl.from_dict(y) for y in obj.get("weatherIconUrl")]
        _winddir16Point = str(obj.get("winddir16Point"))
        _winddirDegree = str(obj.get("winddirDegree"))
        _windspeedKmph = str(obj.get("windspeedKmph"))
        _windspeedMiles = str(obj.get("windspeedMiles"))
        return CurrentCondition(_FeelsLikeC, _FeelsLikeF, _cloudcover, _humidity, _localObsDateTime, _observation_time, _precipInches, _precipMM, _pressure, _pressureInches, _temp_C, _temp_F, _uvIndex, _visibility, _visibilityMiles, _weatherCode, _weatherDesc, _weatherIconUrl, _winddir16Point, _winddirDegree, _windspeedKmph, _windspeedMiles)

@dataclass
class Hourly:
    DewPointC: str
    DewPointF: str
    FeelsLikeC: str
    FeelsLikeF: str
    HeatIndexC: str
    HeatIndexF: str
    WindChillC: str
    WindChillF: str
    WindGustKmph: str
    WindGustMiles: str
    chanceoffog: str
    chanceoffrost: str
    chanceofhightemp: str
    chanceofovercast: str
    chanceofrain: str
    chanceofremdry: str
    chanceofsnow: str
    chanceofsunshine: str
    chanceofthunder: str
    chanceofwindy: str
    cloudcover: str
    humidity: str
    precipInches: str
    precipMM: str
    pressure: str
    pressureInches: str
    tempC: str
    tempF: str
    time: str
    uvIndex: str
    visibility: str
    visibilityMiles: str
    weatherCode: str
    weatherDesc: List[str]
    weatherIconUrl: List[int]
    winddir16Point: str
    winddirDegree: str
    windspeedKmph: str
    windspeedMiles: str

    @staticmethod
    def from_dict(obj: Any) -> 'Hourly':
        _DewPointC = str(obj.get("DewPointC"))
        _DewPointF = str(obj.get("DewPointF"))
        _FeelsLikeC = str(obj.get("FeelsLikeC"))
        _FeelsLikeF = str(obj.get("FeelsLikeF"))
        _HeatIndexC = str(obj.get("HeatIndexC"))
        _HeatIndexF = str(obj.get("HeatIndexF"))
        _WindChillC = str(obj.get("WindChillC"))
        _WindChillF = str(obj.get("WindChillF"))
        _WindGustKmph = str(obj.get("WindGustKmph"))
        _WindGustMiles = str(obj.get("WindGustMiles"))
        _chanceoffog = str(obj.get("chanceoffog"))
        _chanceoffrost = str(obj.get("chanceoffrost"))
        _chanceofhightemp = str(obj.get("chanceofhightemp"))
        _chanceofovercast = str(obj.get("chanceofovercast"))
        _chanceofrain = str(obj.get("chanceofrain"))
        _chanceofremdry = str(obj.get("chanceofremdry"))
        _chanceofsnow = str(obj.get("chanceofsnow"))
        _chanceofsunshine = str(obj.get("chanceofsunshine"))
        _chanceofthunder = str(obj.get("chanceofthunder"))
        _chanceofwindy = str(obj.get("chanceofwindy"))
        _cloudcover = str(obj.get("cloudcover"))
        _humidity = str(obj.get("humidity"))
        _precipInches = str(obj.get("precipInches"))
        _precipMM = str(obj.get("precipMM"))
        _pressure = str(obj.get("pressure"))
        _pressureInches = str(obj.get("pressureInches"))
        _tempC = str(obj.get("tempC"))
        _tempF = str(obj.get("tempF"))
        _time = str(obj.get("time"))
        _uvIndex = str(obj.get("uvIndex"))
        _visibility = str(obj.get("visibility"))
        _visibilityMiles = str(obj.get("visibilityMiles"))
        _weatherCode = str(obj.get("weatherCode"))
        _weatherDesc = [WeatherDesc.from_dict(y) for y in obj.get("weatherDesc")]
        _weatherIconUrl = [WeatherIconUrl.from_dict(y) for y in obj.get("weatherIconUrl")]
        _winddir16Point = str(obj.get("winddir16Point"))
        _winddirDegree = str(obj.get("winddirDegree"))
        _windspeedKmph = str(obj.get("windspeedKmph"))
        _windspeedMiles = str(obj.get("windspeedMiles"))
        return Hourly(_DewPointC, _DewPointF, _FeelsLikeC, _FeelsLikeF, _HeatIndexC, _HeatIndexF, _WindChillC, _WindChillF, _WindGustKmph, _WindGustMiles, _chanceoffog, _chanceoffrost, _chanceofhightemp, _chanceofovercast, _chanceofrain, _chanceofremdry, _chanceofsnow, _chanceofsunshine, _chanceofthunder, _chanceofwindy, _cloudcover, _humidity, _precipInches, _precipMM, _pressure, _pressureInches, _tempC, _tempF, _time, _uvIndex, _visibility, _visibilityMiles, _weatherCode, _weatherDesc, _weatherIconUrl, _winddir16Point, _winddirDegree, _windspeedKmph, _windspeedMiles)

@dataclass
class NearestArea:
    areaName: List[AreaName]
    country: List[Country]
    latitude: str
    longitude: str
    population: str
    region: List[str]
    weatherUrl: List[str]

    @staticmethod
    def from_dict(obj: Any) -> 'NearestArea':
        _areaName = [AreaName.from_dict(y) for y in obj.get("areaName")]
        _country = [Country.from_dict(y) for y in obj.get("country")]
        _latitude = str(obj.get("latitude"))
        _longitude = str(obj.get("longitude"))
        _population = str(obj.get("population"))
        _region = [Region.from_dict(y) for y in obj.get("region")]
        _weatherUrl = [WeatherUrl.from_dict(y) for y in obj.get("weatherUrl")]
        return NearestArea(_areaName, _country, _latitude, _longitude, _population, _region, _weatherUrl)

@dataclass
class Region:
    value: str

    @staticmethod
    def from_dict(obj: Any) -> 'Region':
        _value = str(obj.get("value"))
        return Region(_value)

@dataclass
class Request:
    query: str
    type: str

    @staticmethod
    def from_dict(obj: Any) -> 'Request':
        _query = str(obj.get("query"))
        _type = str(obj.get("type"))
        return Request(_query, _type)

@dataclass
class Root:
    current_condition: List[CurrentCondition]
    nearest_area: List[NearestArea]
    request: List[str]
    weather: List[str]

    @staticmethod
    def from_dict(obj: Any) -> 'Root':
        _current_condition = [CurrentCondition.from_dict(y) for y in obj.get("current_condition")]
        _nearest_area = [NearestArea.from_dict(y) for y in obj.get("nearest_area")]
        _request = [Request.from_dict(y) for y in obj.get("request")]
        _weather = [Weather.from_dict(y) for y in obj.get("weather")]
        return Root(_current_condition, _nearest_area, _request, _weather)

@dataclass
class Weather:
    astronomy: List[Astronomy]
    avgtempC: str
    avgtempF: str
    date: str
    hourly: List[Hourly]
    maxtempC: str
    maxtempF: str
    mintempC: str
    mintempF: str
    sunHour: str
    totalSnow_cm: str
    uvIndex: str

    @staticmethod
    def from_dict(obj: Any) -> 'Weather':
        _astronomy = [Astronomy.from_dict(y) for y in obj.get("astronomy")]
        _avgtempC = str(obj.get("avgtempC"))
        _avgtempF = str(obj.get("avgtempF"))
        _date = str(obj.get("date"))
        _hourly = [Hourly.from_dict(y) for y in obj.get("hourly")]
        _maxtempC = str(obj.get("maxtempC"))
        _maxtempF = str(obj.get("maxtempF"))
        _mintempC = str(obj.get("mintempC"))
        _mintempF = str(obj.get("mintempF"))
        _sunHour = str(obj.get("sunHour"))
        _totalSnow_cm = str(obj.get("totalSnow_cm"))
        _uvIndex = str(obj.get("uvIndex"))
        return Weather(_astronomy, _avgtempC, _avgtempF, _date, _hourly, _maxtempC, _maxtempF, _mintempC, _mintempF, _sunHour, _totalSnow_cm, _uvIndex)

@dataclass
class WeatherDesc:
    value: str

    @staticmethod
    def from_dict(obj: Any) -> 'WeatherDesc':
        _value = str(obj.get("value"))
        return WeatherDesc(_value)

@dataclass
class WeatherIconUrl:
    value: str

    @staticmethod
    def from_dict(obj: Any) -> 'WeatherIconUrl':
        _value = str(obj.get("value"))
        return WeatherIconUrl(_value)

@dataclass
class WeatherUrl:
    value: str

    @staticmethod
    def from_dict(obj: Any) -> 'WeatherUrl':
        _value = str(obj.get("value"))
        return WeatherUrl(_value)

