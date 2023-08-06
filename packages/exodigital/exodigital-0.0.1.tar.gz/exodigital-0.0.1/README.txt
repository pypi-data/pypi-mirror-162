ExoDigital
~~~~~~~~~~
A digital clock displays the weather and temperature of local and global cities 

Features:
-	Display the local time and date of the local pc time zone
-	Display the local time of two styles 24 hours or 12 hours am or pm  
-	Display the live weather and weather shape with descriptions of local and global cites
-	Shows the Fahrenheit F and Celsius C temperature.
-	Customize the date and time and weather function
-	Customize the dark and daylight theme styles.
- its  tool to convert the temperature from Fahrenheit to Celsius or opposite
- its tool to convert from 12 hours to 24 hours or opposite

Usage:
ExoDigital is used for default options or custom settings:
ExoDigital( Dark: False, Is24H=False,IsFahrenheit=False
TimeDispaly:1000msec)

Functions implementing:
- SetTime(hour,minute,seconds)#time is 24H style format from 0-24, its possible to set-hour only, [minutes,second] could be retrieved from a local pc.

- SetDate(month,day) # set Month from 1-12, the day could be set from 1-31,or 30 depends on allowance month criteria.

- SetWeather('city_name')#could be a country name or city and should be a valid name.

- SetWeather_custom('city_name',temperature,wather_index) 
   #wather_index should be from 0-9 as illustrated below:
   0-Unknown or all types.
	1-Sunny.
	2-Cloudy.
	3-Rainy.
	4-Hard rainy.
	5-Snowy.
	6-Thunder rain.
	7-Thunder hard rain.
	8-Thunder.
	9-Partly Cloudy.


Example-1: in this example, the code shows when implementing the code below its displays only the 
date and time of local pc  
Code snapshot:
from exoticwondrous import ExoDigital 
exo = ExoDigital()
r = exo.RunAndWait()
print(r)

Example-2: in this example, the code shows when implementing the code below its displays the live weather of
 selected desire city in Fahrenheit temperature also with a dark (night) theme as well as displays the date and time in 24 formats in the local pc time zone.   
Code snapshot:
from exoticwondrous import ExoDigital 
exo = ExoDigital(True,True,True)
exo.SetWeather('New York')
r = exo.RunAndWait()
print(r)#show any error occurred


Example-3: in this example, the code shows when implementing the code below its displays the custom weather of
 with date and time of local pc time zone.   
Code snapshot:
from exoticwondrous import ExoDigital 
exo = ExoDigital(False,True,True)
exo.SetWeather_custom('New York',25,6)
r = exo.RunAndWait()
print(r)

Example-4: in this example, the code shows when implementing the code below its displays a custom date and time
Code snapshot:
From exoticwondrous import ExoDigital 
exo = ExoDigital()
exo.SetTime(10,10)
exo.SetDate(1,10)
r = exo.RunAndwait()
print(r)

Requirements:
the modules [requests] should be installed automatically during package installation, however, if it's not installed, please install them manually,
-pip install requests

if any error occurred of 'requests' module,try to solve them by install uplink as pre-required module for requests 
-pip install uplink

Questions and comments
Telegram:https://t.me/exoticwondrous
Email:ahmdsmhmmd@gmail.com