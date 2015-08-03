#! /usr/bin/python

# j_buoy.py
# 
#
# Created by Malcolm Monroe on 5/4/15.
# Some of the product are returning an error. Here is the list of product and if they threw an error.
#water_level = error
#air_temperature = success
#water_temperature = success
#wind = success
#air_pressure = success
#air_gap = error
#conductivity = success
#visibility = error
#humidity = error
#salinity = success
#hourly_height = error
#high_low = error
#daily_mean = error
#monthly_mean = error
#one_minute_water_level = error
#predictions = error
#currents = error

import requests
import json
import time
import sys
import optparse

'''
'''
PRODUCT_POINTS = {
  'wind':{'dr':'wind_direction', 'd':'wind_swell', 'g':'wind_wind_gust','s':'wind_speed'},
  'salinity':{'s':'salinity', 'g': 'salinity-specific_gravity'},
  'conductivity': {'v':'conductivity', 'lat': 'latitude', 'lon': 'longitude'},
  'water_level': {'v':'water_level'},
  'air_temperature':{'v':'air_temperature'}, 
  'water_temperature':{'v':'water_temperature'}, 
  'air_pressure':{'v':'air_pressure'}, 
  'air_gap':{'v':'air_gap'}, 
  'visibility':{'v':'visibility'}, 
  'humidity':{'v':'humidity'}, 
  'hourly_height':{'v':'hourly_height'}, 
  'high_low':{'v':'high_low'}, 
  'daily_mean':{'v':'daily_mean'}, 
  'monthly_mean':{'v':'monthly_mean'}, 
  'one_minute_water_level':{'v':'one_minute_water_level'}, 
  'predictions':{'v':'predictions'}, 
  'currents':{'v':'currents'},
}

def get_json_readings(product, json_data, metaData):
  points = PRODUCT_POINTS[product]

  readings = []
  for data in json_data:
    for key, meterId in points.items():
      timestamp = ''.join([data['t'].replace(' ', 'T'), ':00+00:00'])
      try:
        value = data[key]
      except KeyError:
        value = metaData[key]

      readings.append({
        'meterId':meterId,
        'timestamp':timestamp,
        'value':value
      })
  return readings


def get_meterCatalog(product, metaData):
  points = PRODUCT_POINTS[product]
  meterCatalog = []
  for key, value in points.items():
    meterCatalog.append({
      'meterId':value,
      'meterName': '%s (%s)' % (metaData['name'], value)
    })
  return meterCatalog

def get_json_object(datasource, readings, catalog):
  json_obj_out = {'expectedDataResolution':'6', 'datasource':datasource, "readings": readings,"meterCatalog": catalog}
  return json.dumps(json_obj_out, sort_keys=True, indent=2)

def get_json_error(error):
  with open ('/var/log/dashboard/error_log.txt', 'a') as errorFile:
    errorFile.write(error)

def main():
    
  parser = optparse.OptionParser('usage %prog '+\
                              '--s1 <stationID1> --s2 <stationID2')
  parser.add_option('--s1', dest = 'sID1', type ='string', \
                        help = 'Specify station #1 for data grab.')
  parser.add_option('--s2', dest = 'sID2', type ='string', \
                        help = 'Specify station #2 for data grab.')
  parser.add_option('--s3', dest = 'sID3', type ='string', \
                        help = 'Specify station #3 for data grab.')
  parser.add_option('--s4', dest = 'sID4', type ='string', \
                        help = 'Specify station #4 for data grab.')
  parser.add_option('--s5', dest = 'sID5', type ='string', \
                        help = 'Specify station #5 for data grab.')
  (options, args) = parser.parse_args()
  staions = []
  stations.extend((options.sID1, options.sID2, options.sID3, options.sID4, options.sID5))
  meterCatalog = []
  readings = []

  for station in stations:
    for product in PRODUCT_POINTS.keys():
      url = 'http://tidesandcurrents.noaa.gov/api/datagetter?range=1&' \
        'station=%(station)s&product=%(product)s&' \
        'units=english&time_zone=gmt&application=lucid&format=json' % ({'station':station, 'product':product})

      try:
        response = requests.get(url)
      except requests.exceptions.ConnectionError as ce:
        get_json_error('Unable to access URL %s [%s]\n\n' % (url, ce))
        continue

      try:
        json_obj = response.json()
      except ValueError as ve:
        get_json_error('JSON is not correctly formed [%s]' % ve)
        continue

      # DATA is stored here ie. timestamps, values, units
      # MetaDATA is stored here (Metadata = lat, lon, id, name
      if 'error' in json_obj:
        error = json_obj['error']
        errorMessage = "\n(%s @%s) / STATION: %s / POINT: %s / Error: %s\n" % (
          time.strftime("%d/%m/%Y"), time.strftime("%H:%M:%S"), id, product, error['message']
        )
        get_json_error(errorMessage)
        continue

      json_obj_metadata = json_obj['metadata']
      meterCatalog.extend(get_meterCatalog(product, json_obj_metadata))
      readings.extend(get_json_readings(product, json_obj['data'], json_obj_metadata))
    json_obj_out = get_json_object('bos://buildingos-json/ju', readings, meterCatalog)

    resp = requests.post('https://rest.buildingos.com/json/readings/', files={'data':('readings.json', json_obj_out)})
    #print resp.text
main()
