#
#   Created by Ryan McDermott
#   Created on 6/13/2022
#

import json
from google.cloud import tasks_v2
from indxdatalaketools.GoogleClientWrappers import CloudTasks

HOLDING_TABLE_URL = 'https://patients-db-api-6vyiigtwia-uc.a.run.app'

class Client:
    '''
        Class that contains all the functionality make a call to the 
        internal Cloud Run API service
    '''
    __cloud_tasks_client    = None
    __cloud_tasks_wrapper   = None

    def __init__(self, google_clients):
        '''
            Init function that sets up client credentials and uuid, 
            Args:
                google_clients          (ApiClients): object containing all Google Api Clients
            Returns:
                None
        '''
        self.__cloud_tasks_client = google_clients.cloud_tasks_client
        self.__cloud_tasks_wrapper = CloudTasks.Wrapper(google_clients)

    

    def create_holding_table_if_not_exist(self, table_data):
        '''
            Function that creates a cloud sql table if it does not already exist
            Args:
                - table_data (dict): The values of the table to create
            Returns:
                - boolean: True if the table got created false if otherwise
        '''
        payload = json.dumps(table_data)
        parent  = self.__cloud_tasks_client.\
            queue_path("indx-data-services", "us-central1", "PATIENTS-holding-table-flush")
        task    = {
            "http_request": {  # Specify the type of request.
                "http_method": tasks_v2.HttpMethod.POST,
                "url": 'https://patients-db-api-6vyiigtwia-uc.a.run.app/patientTable',  # The full url path that the task will be sent to.
                "oidc_token": {
                    "service_account_email": 'patients-holding-table@indx-data-services.iam.gserviceaccount.com',
                    "audience": 'https://patients-db-api-6vyiigtwia-uc.a.run.app'
                }
            }
        }

        task["http_request"]["headers"] = {"Content-type": "application/json"}
        converted_payload               = payload.encode()
        task["http_request"]["body"]    = converted_payload

        return self.__cloud_tasks_wrapper.create_http_task(parent, task)



    def delete_holding_table(self, client_id):
        '''
            Function that deletes a cloud sql table if it does not already exist
            Args:
                - table_data (dict): The values of the table to create
            Returns:
                - boolean: True if the table got created false if otherwise
        '''
        parent  = self.__cloud_tasks_client.\
            queue_path("indx-data-services", "us-central1", "PATIENTS-holding-table-flush")
        task    = {
            "http_request": {  # Specify the type of request.
                "http_method": tasks_v2.HttpMethod.DELETE,
                "url": 'https://patients-db-api-6vyiigtwia-uc.a.run.app/patientTable/'+client_id,  # The full url path that the task will be sent to.
                "oidc_token": {
                    "service_account_email": 'patients-holding-table@indx-data-services.iam.gserviceaccount.com',
                    "audience": 'https://patients-db-api-6vyiigtwia-uc.a.run.app'
                }
            }
        }

        return self.__cloud_tasks_wrapper.create_http_task(parent, task)


    def insert_data_to_holding_table(self, patient_data):
        '''
            Function that inserts patient data to the holding table. If
                the patient record already exists, it is updated.
            Args:
                - patient_data (dict): The values of the patient to create
            Returns:
                - boolean: True if the patient data was created, False if otherwise
        '''
        client_id = patient_data['client-id']
        payload = json.dumps(patient_data)
        parent  = self.__cloud_tasks_client.\
            queue_path("indx-data-services", "us-central1", "PATIENTS-holding-table-flush")
        task    = {
            "http_request": {  # Specify the type of request.
                "http_method": tasks_v2.HttpMethod.POST,
                "url": 'https://patients-db-api-6vyiigtwia-uc.a.run.app/patientEntry/'+client_id,  # The full url path that the task will be sent to.
                "oidc_token": {
                    "service_account_email": 'patients-holding-table@indx-data-services.iam.gserviceaccount.com',
                    "audience": 'https://patients-db-api-6vyiigtwia-uc.a.run.app'
                }
            }
        }

        task["http_request"]["headers"] = {"Content-type": "application/json"}
        converted_payload               = payload.encode()
        task["http_request"]["body"]    = converted_payload

        return self.__cloud_tasks_wrapper.create_http_task(parent, task)


    