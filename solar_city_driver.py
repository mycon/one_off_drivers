import requests
import json
import base64
import pprint
import datetime as dt 
from datetime import timedelta
from client_cradentials import get_solar_city_cradentials

    # ---- Driver Proof of Concept - Solar City API Boulder Valley School Distirct ------------

          
def get_polling_date_times():
  poll_times = []
  todays_date = dt.date.today()
  current_datetime = dt.datetime.now()
  todays_time = current_datetime.time()
  previous_date = todays_date - timedelta(1)
  delta  = dt.timedelta(minutes=15)
  offset_time = (dt.datetime.combine(dt.date(1,1,1),todays_time) - delta).time()
  end_datetime = "%sT%s" % (todays_date.strftime('%Y-%m-%d'), todays_time.strftime('%H:%M:%S'))
  start_datetime = "%sT%s" % (todays_date.strftime('%Y-%m-%d'), offset_time.strftime('%H:%M:%S'))
  poll_times.append(start_datetime)
  poll_times.append(end_datetime)
  return poll_times


def get_error_json(error):
  with open ('/users/malcolmmonroe/desktop/error_log.txt', 'a') as errorFile:    
    errorFile.write(error)


def get_meter_catalog(measurements, id, job_id, meter_catalog):
  for measurement in measurements:
    if measurement != 'Timestamp' and measurement != 'DataStatus':
      catalog = {'meterId': '%s_%s_%s' % (measurement, id.replace('-', ''), job_id.replace('-', '')), 'meterName': measurement, 'meterDescription': job_id.replace('-', '')}
      meter_catalog.append(catalog)
  return meter_catalog


def get_readings_catalog(data, measurements, id, job_id, readings):
  for measurement in measurements:
    if measurement != 'Timestamp' and measurement != 'DataStatus':
      catalog = {'timestamp': data[0]['Timestamp'] , 'value': data[0][measurement], 'meterId': '%s_%s_%s' %(measurement, id.replace('-', ''), job_id.replace('-', ''))}
      readings.append(catalog)
  return readings 

class SolarCityRequests(object)
  def __init__(self, token):
      self.token = token
      self.access_header = {'Authorization':'Basic '+ base64.b64encode(cradentials['clientID']+':'+cradentials['client_secret'])}
      self.request_header = {'Authorization':'Bearer '+self.token}

  def get_access_token(self):
      try:


'''class CustomerData(object):
        def __init__(self, token):
        self.token = token
        self.headers = {'Authorization':'Bearer '+self.token}


    def get_customer_records(self): 
        resp = requests.get('https://api.solarcity.com/powerguide/v1.0/customers', headers=self.headers)
        records = resp.json()['Data']
        customer_GUIDS = [records[customer]['GUID'] for customer in range(len(records))]
        customer_names = [records[customer]['CustomerName'] for customer in range(len(records))]
        self.customer_details = {'customer': customer_names, 'id': customer_GUIDS}
        return self.customer_details


    def get_customer_install_ids(self):
        resp = requests.get('https://api.solarcity.com/powerguide/v1.0/installations/', headers= self.headers)
        installs = resp.json()['Data']
        install_IDS = [installs[install]['GUID'] for install in range(len(installs))]
        install_jobIDS =[installs[install]['JobID'] for install in range(len(installs))]
        customer_installs = []
        for id in range(len(self.customer_details['id'])):
            resp = requests.get('https://api.solarcity.com/powerguide/v1.0/customers/'+self.customer_details['id'][id], 
                                 headers=self.headers, 
                                 params = {'IsDetailed':'true'})
            install_GUIDS = resp.json()['Installations']

            for num in range(len(install_GUIDS)):
                GUID = install_GUIDS[num]['GUID']
                
                if GUID in  install_IDS:
                    pos = install_IDS.index(GUID)
                    install_GUIDS[num]['JobID'] = install_jobIDS[pos]

            customer_install = {'customer': self.customer_details['customer'][id], 'installs': install_GUIDS}
            customer_installs.append(customer_install) 
        
        return customer_installs '''



    #-----API credentials provided by Solar City (Access to API is for partners only)-----------
def main(): 
    #------for scalable integration USERNAME and PASSWORD will need to be a user input--------#
    cradentials = get_solar_city_cradentials()

    auth_data = {'grant_type': 'password',
               'username': cradentials['username'],
               'password': cradentials['password'],
               'scope': cradentials['scope']}
    print auth_data

     #---------Request for authorization token----------
    
    
    access_token = resp.json()['access_token']
    headers = {'Authorization':'Bearer '+access_token}
    print access_token


    #--------Request list of customer records - Note the below header will be used for all requests to follow-------------
    '''customer_info = CustomerData(access_token)
    customer_meta = customer_info.get_customer_records()
    customer_installs = customer_info.get_customer_install_ids()
    sample_times = get_polling_date_times()
    readings = []
    meter_catalog = []
   
    for customer in range(len(customer_installs)):
        for install in range(len(customer_installs[customer]['installs'])):
            GUID = customer_installs[customer]['installs'][install]['GUID']
            jobID = customer_installs[customer]['installs'][install]['JobID']
            url_production = 'https://api.solarcity.com/powerguide/v1.0/measurements/'+GUID
            production_response = requests.get(url_production, headers=headers, params = {'StartTime': '%s' % sample_times[0], 
                                        'EndTime': '%s' % sample_times[1], 
                                        'Period': 'Quarterhour', 
                                        'IsByDevice': 'true'})
           
           

            try:
                json_obj_prod = production_response.json()
            except Exception as e:
                get_error_json("Unable to access url @ %s: %s [%s] \n \n" % (dt.datetime.now().strftime('%Y-%m-%dT%H-%M-%S'), url_production, e))  #Path to error log needs to be changed
                continue

            try:
                production_data = json_obj_prod['Devices'][0]['Measurements']
            except KeyError:
                print "We are here at the moment"
                get_error_json("Unexpected JSON returned from %s @ %s: %s" % (url_production, dt.datetime.now().strftime('%Y-%m-%dT%H-%M-%S'), json_obj_prod))
                continue

            prod_keys = production_data[0].keys()
            get_meter_catalog(prod_keys, GUID, jobID, meter_catalog)
            get_readings_catalog(production_data, prod_keys, GUID, jobID, readings)
         
            
    for customer in range(len(customer_installs)):
        for install in range(len(customer_installs[customer]['installs'])):
            GUID = customer_installs[customer]['installs'][install]['GUID']
            jobID = customer_installs[customer]['installs'][install]['JobID']
            url_consumption = 'https://api.solarcity.com/powerguide/v1.0/consumption/'+GUID
            consumption_response = requests.get(url_consumption, headers=headers, params = {'StartTime': '%s' % sample_times[0], 
                                        'EndTime': '%s' % sample_times[1], 
                                        'Period': 'Quarterhour', 
                                        'IsByDevice': 'true'})

            try:
                json_obj_consumption = consumption_response.json()
            except Exception as e:
                get_error_json("Unable to access url @ %s: %s [%s] \n \n" % (dt.datetime.now().strftime('%Y-%m-%dT%H-%M-%S'), url_consumption, e))  #Path to error log needs to be changed
                continue

            try:
                consumption_data = json_obj_consumption['Consumption']
                consumption_keys = consumption_data[0].keys()
                meterCatalog = get_meter_catalog(consumption_keys, GUID, jobID, meter_catalog)
                readings = get_readings_catalog(consumption_data, consumption_keys, GUID, jobID, readings)
            except KeyError:
                get_error_json("Unexpected JSON from %s @ %s: %s" % (url_consumption, dt.datetime.now().strftime('%Y-%m-%dT%H-%M-%S'), json_obj_consumption))
                continue
        
        catalog = {'datasource': 'bos://buildingos-json/bvsd_test', 'expectedDataResolution': '15', 'meterCatalog': meterCatalog, 'readings': readings}
        meter_Catalog = json.dumps(catalog)
    print catalog
    response = requests.post('https://rest.buildingos.com/json/readings/', data=meter_Catalog)'''


main()

















