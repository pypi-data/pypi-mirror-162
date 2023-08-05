#
#   Created By Ryan McDermott
#   Created on 2/23/2022
#

from google.api_core.exceptions import NotFound
from indxdatalaketools import Helpers

class Validator:
    '''
        class that validates the Client Id for a command. Different commands require
        different forms of validation.
    '''
    client_uuid                         = ''
    data_lake_command                   = ''
    credentials_file_path               = ''

    __client_id_validation_functions    = None
    __google_datastore_client           = None
    __google_cloud_storage_client       = None
    __google_bigquery_client            = None


    def __init__(self, google_clients):

        self.__google_datastore_client      = google_clients.datastore_client
        self.__google_bigquery_client       = google_clients.big_query_client
        self.__google_cloud_storage_client  = google_clients.cloud_storage_client

        self.__set_up_client_id_validation_functions()


    def __set_up_client_id_validation_functions(self):
        '''
            Sets up the mapping from the command passed to the function that will validate
            the client_id
            Args:
                None
            Returns:
                None
        '''
        self.__client_id_validation_functions = {
            'datalake': self.__validate_client_is_in_datastore,
            'snapshot': self.__validate_primary_and_snapshot_buckets,
            'patients-table': self.__validate_dataset_and_table,
            'file': self.__validate_primary_bucket,
            'file update': self.__validate_primary_bucket
        }
        

    def close(self):
        '''
            Frees and destroys all allocated resources
            Returns:
                None
        '''
        self.__google_cloud_storage_client.close()
        self.__google_datastore_client.close()
        self.__google_bigquery_client.close()


    def validate(self, client_uuid, data_lake_command):
        '''
            Validates the client ID
            Returns:    
                boolean: True if the client id is valid, False if otherwise
        '''
        self.client_uuid = client_uuid
        return self.__client_id_validation_functions[data_lake_command]()


    def __validate_client_is_in_datastore(self):
        '''
            Verifies the client id exists in Datastore      
            Returns:
                boolean: True if the client id is valid, False if otherwise
        '''
        key                 = self.__google_datastore_client.key('Client', self.client_uuid)
        entity              = self.__google_datastore_client.get(key=key)

        # Validate Client entity exists, exit if not
        if entity is None:
            Helpers.print_error(self.client_uuid + " does not exist in datastore: not a valid CLIENT_ID")
            return False
        
        return True


    def __validate_primary_and_snapshot_buckets(self):
        '''
            Verifies the client id primary bucket exists and well as the snapshot bucket
            Returns:
                boolean: True if the client id is valid, False if otherwise
        '''
        
        data_lake_snapshot_bucket   = self.__google_cloud_storage_client.\
            bucket(self.client_uuid + '-snapshots')

        if not Helpers.try_bucket_exists(data_lake_snapshot_bucket):
            Helpers.print_error('DataLake snapshot bucket does not exist: Bad Request')
            return False

        return self.__validate_primary_bucket()


    def __validate_primary_bucket(self):
        '''
            Verifies the client id primary bucket exists and well as the snapshot bucket
            Returns:
                boolean: True if the client id is valid, False if otherwise
        '''
        data_lake_bucket            = self.__google_cloud_storage_client.\
            bucket(self.client_uuid)

        if not Helpers.try_bucket_exists(data_lake_bucket):
            Helpers.print_error('DataLake bucket does not exist: Bad Request')
            return False

        return True

    
    def __validate_dataset_and_table(self):
        '''
            Verifies the client id dataset and PAETIENTS table exists
            Returns:
                boolean: True if the client id is valid, False if otherwise
        '''
        client_id_conformed_name    = self.client_uuid.replace('-','_')
        dataset_id                  = 'indx-data-services.'+ client_id_conformed_name
        table_id                    = dataset_id + '.PATIENTS'

        if not self.__check_if_dataset_exists(dataset_id):
            Helpers.print_error('Dataset for clientId does not exist: Bad Request')
            return False

        if not self.__check_if_table_exists(table_id):
            Helpers.print_error('PATIENTS table does not exist: Bad Request')
            return False

        return True


    def __check_if_table_exists(self, table_id):
        '''
            Checks if the table Id passed exists on GCP
            Args:
                dataset_id (string): The table {PROJECT_ID}.{DATASET}.PATIENTS
            Returns:
                boolean: True if the table exists, false if other wise
        '''
        try:
            self.__google_bigquery_client.get_table(table_id)  # Make an API request.
            return True
        except NotFound:
            return False

    def __check_if_dataset_exists(self, dataset_id):
        '''
            Checks if the dataset ID passed exists on GCP
            Args:
                dataset_id (string): The dataset {PROJECT_ID}.{CLIENT_UUID}
            Returns:
                boolean: True if the datset exists, false if other wise
        '''
        try:
            self.__google_bigquery_client.get_dataset(dataset_id)  # Make an API request.
            return True
        except NotFound:
            return False