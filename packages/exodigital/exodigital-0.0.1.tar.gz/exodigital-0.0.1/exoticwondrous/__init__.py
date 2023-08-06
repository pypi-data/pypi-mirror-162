from asyncio.windows_events import NULL
from ctypes import c_bool, c_double, c_int, c_uint, WINFUNCTYPE, windll
from ctypes.wintypes import HWND, LPCWSTR, UINT
from gettext import find
import struct
from urllib import request
import requests 
import  exoticwondrous.jsonex
import json
import os

# ExoDigital from exoticwondrous
# Telegram: https//exoticwondrous
# Ahmed Mohammmed
# ahmdsmhmmd@gmail.com   

class ExoDigital: 
         __xLoad = NULL
         def __init__(self, __theme=0, __Is24H=False,__IsFahrenheit=False,__TimeoutDelay=1000 ):
              self.__theme = __theme
              self.__Is24H = __Is24H
              self.__IsFahrenheit = __IsFahrenheit
              self.__TimeoutDelay = __TimeoutDelay

              if (struct.calcsize("P")==8):    
                  dllname=str(os.path.dirname(__file__)) + '\\exodigitl.dll'
              else: dllname=str(os.path.dirname(__file__)) + '\\exodigitl32.dll'

              self.__showmsg("finding package exiting: " + str(os.path.isfile(dllname)))

              try:  
                    __xLoad = windll.LoadLibrary(dllname)
              except:
                 self.__showmsg('Error:cannot loading required files to run digialtclock')     

              __ExoCMain = WINFUNCTYPE(c_int,c_bool,c_bool,c_bool,c_int)
              __Weather = WINFUNCTYPE(c_int,LPCWSTR)
              __Weather_custom = WINFUNCTYPE(c_int,LPCWSTR,c_double,c_int)
              __Date_custom = WINFUNCTYPE(c_int,c_int,c_int)
              __Time_custom = WINFUNCTYPE(c_int,c_int,c_int,c_int)

              if __xLoad !=NULL:
                    self.__rundigitclock = __ExoCMain(("ExoDigitCMain",__xLoad))
                    self.__weather = __Weather(("weatherfromJosn",__xLoad))
                    self.__weather_custom = __Weather_custom(("weather_custom",__xLoad))      
                    self.__date_custom = __Date_custom(("date_custom",__xLoad))
                    self.__time_custom = __Time_custom(("time_custom",__xLoad))
              else:
                    self.__showmsg("Error: cannot get instance of __xload object: is equal to null")       
 
         def   __getweather__ (self,city):
               url = 'https://wttr.in/{}?format=j1'.format(city)
               txt =  requests.get(url).text
               jso = json.loads(txt)
               return   exoticwondrous.jsonex.Root.from_dict(jso)
         def __showmsg(self,prt):
               print(prt)
               
         def RunAndWait(self): 
              ret = self.__rundigitclock(self.__theme,self.__Is24H,self.__IsFahrenheit,self.__TimeoutDelay)
              if ret== 0:
                  return 'launch digital clock...' 
              if ret == -1:
                   return 'Error: not valid weather value set'
              if ret ==-2: 
                   return 'Error: not valid delay set, is should be from 0-30000 millisecond'
              if ret == -3:
                   return  'Error not valid date set, please check custom date set'       
              if ret == -4:
                  return 'Error not valid time set, please check custom time set' 
              if ret == -5:
                   return 'Error not valid custom weather index set it should be from 0 to 9 only'
              if ret == -6:
                   return   'Error not valid weather data setup!'
              

         def SetWeather(self,city_name):
              self.__showmsg('Done.\nInitialize...')
              self.__showmsg('checking internet connection...Please wait...')
              try:
                 root = self.__getweather__(city_name)
                 self.__showmsg('Done.')
                 return self.__weather(str(root.nearest_area[0].country)+"*"+city_name+'-'+str(root.nearest_area[0].region)+'*'+str(root.current_condition[0].FeelsLikeC)+'*'+ str(root.current_condition[0].weatherCode+'*'+str(root.current_condition[0].weatherDesc))) 
              except Exception as e:
                 if str(e).find('HTTPSConnectionPool')!=-1 or str(e).find('Connection aborted.')!=-1:
                    self.__showmsg('Error: cannot connect to live weather server! Please check your internet connection and try again')
                 elif str(e).find('NoneType')!=-1:
                    self.__showmsg('Error: cannot find city name or data cannot set correctly')
                 else:
                    self.__showmsg('Error: package-module might be corrupted,Please request pip uninstall  \'exodigital\' then type pip install  \'exodigital\' again')  

         def SetDate(self,Day, Month):
              return self.__date_custom(Day,Month)
          
         def SetTime(self, Hour,Minute=-1,Second=-1):
              return self.__time_custom(Hour,Minute,Second)

         def SetWeather_custom(self,city_name,temperature,weather_index):
             return self.__weather_custom(city_name,temperature,weather_index)
