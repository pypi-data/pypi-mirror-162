#
#   Created by Ryan McDermott
#   Created on 3/2/2022
#

import google.auth

from google.cloud import storage
from google.cloud import bigquery
from google.cloud import bigquery_storage_v1
from google.cloud import datastore
from google.cloud import pubsub_v1
from google.cloud import scheduler_v1
from google.cloud import tasks_v2
from google.cloud import secretmanager

from google.oauth2 import service_account
from google.cloud.compute_v1.services import instances
from google.cloud.compute_v1.services import zone_operations

class ApiClients:
    ''' Data Structure that hold all google API clients '''
    
    credentials                = ''
    scopes                          = ['https://www.googleapis.com/auth/cloud-platform']
    cloud_storage_client            = None
    big_query_client                = None
    secret_manager_client           = None
    big_query_storage_v1_client     = None
    datastore_client                = None
    pubsub_v1_client                = None
    cloud_tasks_client              = None
    cloud_scheduler_client          = None
    compute_engine_instance_client  = None
    compute_engine_operation_client = None
    account_credentials             = None
    account_googleapiclient         = None

    def __init__(self, credentials_file=None):
        '''
            Initializes all google api clients used in the data lake tools
            Args:
                credentials (string): The file path to the service acount key, or None
                    to use the default credentials
            Returns:
                None
        '''
        
        self.credentials = credentials_file
        
        if credentials_file is None:
            self.cloud_storage_client               = storage.Client()
            self.big_query_client                   = bigquery.Client()
            self.big_query_storage_v1_client        = bigquery_storage_v1.BigQueryWriteClient()
            self.secret_manager_client              = secretmanager.SecretManagerServiceClient()
            self.datastore_client                   = datastore.Client()
            self.pubsub_v1_client                   = pubsub_v1.PublisherClient()
            self.cloud_scheduler_client             = scheduler_v1.CloudSchedulerClient()
            self.compute_engine_instance_client     = instances.InstancesClient()
            self.compute_engine_operation_client    = zone_operations.ZoneOperationsClient()
            self.account_credentials, project       = google.auth.default()
            self.cloud_tasks_client                 = tasks_v2.CloudTasksClient()
            
        else:
            self.cloud_storage_client               = storage.Client.\
                from_service_account_json(credentials_file)
            self.big_query_client                   = bigquery.Client.\
                from_service_account_json(credentials_file)
            self.big_query_storage_v1_client        = bigquery_storage_v1.BigQueryWriteClient.\
                from_service_account_json(credentials_file)
            self.secret_manager_client              = secretmanager.SecretManagerServiceClient.\
                from_service_account_json(credentials_file)
            self.datastore_client                   = datastore.Client.\
                from_service_account_json(credentials_file)
            self.pubsub_v1_client                   = pubsub_v1.PublisherClient.\
                from_service_account_json(credentials_file)
            self.cloud_scheduler_client             = scheduler_v1.CloudSchedulerClient.\
                from_service_account_json(credentials_file)
            self.compute_engine_instance_client    = instances.InstancesClient.\
                from_service_account_json(credentials_file)
            self.compute_engine_operation_client    = zone_operations.ZoneOperationsClient.\
                from_service_account_json(credentials_file)
            self.account_credentials                = service_account.Credentials.\
                from_service_account_file(filename=credentials_file, scopes=self.scopes)
            self.cloud_tasks_client                 = tasks_v2.CloudTasksClient.\
                from_service_account_json(credentials_file)


    



