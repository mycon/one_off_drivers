import requests
import json
import base64
import pprint
from datetime import datetime, timedelta
from datetime import timedelta
from client_cradentials import get_solar_city_cradentials
import sys

    # ---- Driver Proof of Concept - Solar City API Boulder Valley School Distirct ------------

          



def get_error_json(error):
  with open ('/users/malcolmmonroe/desktop/error_log_scr.txt', 'a') as errorFile:    
    errorFile.write('%s: ERROR Timestamp(%s)' % (error, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


class JSONCreater(object):

  def __init__(self, customer_data):
    self.customer_data = customer_data


  def get_meter_catalog(self):
    meter_catalog = []
    for install in range(len(self.customer_data)):
      for measurement in self.customer_data[install]['data'][0].keys():
        if measurement != 'Timestamp' and measurement != 'DataStatus':
          catalog = {'meterId': '%s_%s_%s' % (measurement, self.customer_data[install]['GUID'].replace('-', ''), self.customer_data[install]['JobID'].replace('-', '')), 
                     'meterName': measurement, 
                     'meterDescription': self.customer_data[install]['JobID'].replace('-', '')}
          meter_catalog.append(catalog)
    return meter_catalog


  def get_meter_readings(self):
    readings = []
    for install in range(len(self.customer_data)):
      for reading in self.customer_data[install]['data']:
        for measurement in self.customer_data[install]['data'][0].keys():
          if measurement != 'Timestamp' and measurement != 'DataStatus':
            catalog = {'timestamp': reading['Timestamp'] , 
                       'value': reading[measurement], 
                       'meterId': '%s_%s_%s' %(measurement, self.customer_data[install]['GUID'].replace('-', ''), self.customer_data[install]['JobID'].replace('-', ''))}
            readings.append(catalog)
    return readings 


class SolarCityRequests(object):

  def __init__(self, auth_params):
    self.auth_params = auth_params
    self.access_headers = {'Authorization':'Basic '+ base64.b64encode(self.auth_params['CLIENTID']+':'+self.auth_params['CLIENT_SECRET'])}
    
  def request_access_token(self):
    url = 'https://login.solarcity.com/issue/oauth2/token'
    for attempt in range(0, 3):
      try:
        response = requests.post(url, headers=self.access_headers, data=self.auth_params['auth_params'])
        break
      except requests.exceptions.ConnectionError as re:
        get_error_json("Unable to access URL %s [%s] \n\n" % (url, re))
        continue
      
    try:
      json_obj = response.json()
    except ValueError as ve:
      get_error_json("JSON is not correctly formed [%s]" % ve)

      if 'Message' in json_obj:
        get_json_error(json_obj['Message'])
        sys.exit("Invalid JSON returned with no access token.")
    
    self.access_token = json_obj['access_token']
    self.request_headers = {'Authorization': 'Bearer '+self.access_token}
    return self.access_token

  def request_customer_installs(self):
    url ='https://api.solarcity.com/powerguide/v1.0/installations/'
    for attempt in range(0, 3):
      try:
        response = requests.get(url, headers= self.request_headers)
        #print response
        break
      except requests.exceptions.RequestException as re:
        get_error_json("Unable to access URL %s [%s] \n\n" % (url, re))
        continue

    try:
      json_obj = response.json()
    except ValueError as ve:
      if 'Message' in json_obj:
        get_json_error(json_obj['Message'])
        sys.exit("Invalid JSON returned, with customer installs.")
    self.customer_installs = json_obj['Data']
    return self.customer_installs

  def request_customer_production_data(self):
    end_time = datetime.now().strftime('%Y-%m-%dT%H:%H:%S')
    start_time = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%dT%H:%H:%S')
    customer_interval_prod_data = []
    for install in range(len(self.customer_installs)):      
      GUID = self.customer_installs[install]['GUID']
      jobID = self.customer_installs[install]['JobID']
      url = 'https://api.solarcity.com/powerguide/v1.0/measurements/'+GUID
      for attempt in range(0, 3):
        try:
          response = requests.get(url, headers=self.request_headers, params = {'StartTime': '%s' % start_time, 
                                                                  'EndTime': '%s' % end_time, 
                                                                  'Period': 'Quarterhour', 
                                                                  'IsByDevice': 'true'})
          #print response
          break
        except requests.exceptions.RequestException as re:
          get_error_json("Unable to access URL %s [%s] \n\n" % (url, re))
          continue
           
      try:
        json_obj = response.json()
      except ValueError as ve:
        get_error_json("JSON is not correctly formed [%s]" % ve)
        if 'Message' in json_obj:
          get_error_json(json['Message'])
        continue

      try:
        interval_data = json_obj['Devices'][0]['Measurements']
      except KeyError:
        get_error_json("Unexpected JSON returned from %s @ %s: %s" % (url_production, dt.datetime.now().strftime('%Y-%m-%dT%H-%M-%S'), json_obj_prod))
        continue

      production_data = {'GUID': GUID, 'JobID': jobID, 'data': interval_data}
      customer_interval_prod_data.append(production_data)
    return customer_interval_prod_data











    #-----API credentials provided by Solar City (Access to API is for partners only)-----------
def main(): 
    #------for scalable integration USERNAME and PASSWORD will need to be a user input--------#
    credentials = get_solar_city_cradentials()

    auth_data = {'CLIENTID': credentials['clientID'], 
                 'CLIENT_SECRET': credentials['client_secret'],
                 'auth_params': {'grant_type': 'password',
                 'username': credentials['username'],
                 'password': credentials['password'],
                 'scope': credentials['scope']}}
 

     #---------Request for authorization token----------
    scr_requester = SolarCityRequests(auth_data)
    token = scr_requester.request_access_token()
    customer_installs = scr_requester.request_customer_installs()
    meter_catalog = []
    readings_catalog = []

    customer_produciton_data = JSONCreater(scr_requester.request_customer_production_data())
    meterCatalog = customer_produciton_data.get_meter_catalog()
    readings = customer_produciton_data.get_meter_readings()
    
    catalog = {'datasource': 'bos://buildingos-json/bvsd_test', 'expectedDataResolution': '15', 'meterCatalog': meterCatalog, 'readings': readings}
    meter_Catalog = json.dumps(catalog)
    response = requests.post('https://rest.buildingos.com/json/readings/', data=meter_Catalog)
    


if __name__ == "__main__":  
  main()

















