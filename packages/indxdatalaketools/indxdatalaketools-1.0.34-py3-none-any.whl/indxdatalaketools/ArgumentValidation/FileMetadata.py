#
#   Created by Ryan McDermott
#   Created on 2/24/2022
#

import datetime
import re
from indxdatalaketools import Helpers
from indxdatalaketools.ArgumentValidation import ValidationHelpers
from indxdatalaketools.DataLakeGlobals import TIME_REGEX
from indxdatalaketools.PropertiesDBApi import Properties

IN_METADATA = ' in metadata'

class Validator:
    '''
        Class that validates the File metadata fields passed by the client
    '''
    client_uuid                         = ''
    data_lake_command                   = ''
    arguments                           = {}
    metadata                            = {}
    
    __metadata_validation_functions     = None
    __google_storage_client             = None

    def __init__(self, google_clients):
        
        
        self.__google_storage_client    = google_clients.cloud_storage_client

        self.__set_up_metadata_validation_functions()


    def __set_up_metadata_validation_functions(self):
        '''
            Sets up the mapping from the arguments passed in patient_data 
            to the function that will validate the given field
            Args:
                None
            Returns:
                None
        '''
        self.__metadata_validation_functions = {
            'CLIENT_ID': self.__validate_client,
            'PATIENT_ID': self.__validate_patient_id,
            'MODALITY': self.__validate_modality,
            'FILE_PATH': self.__validate_file_path,
            'DATE_OF_SERVICE': ValidationHelpers.validate_date,
            'TIME_OF_SERVICE': self.__validate_time_of_service,
            'LOCATION_OF_SERVICE': self.__validate_location_of_service,
            'SOURCE': self.__validate_source,
            'ORIGINATOR': self.__validate_originator
        }

    
    def close(self):
        '''
            Frees and destroys all allocated resources
            Returns:
                None
        '''
        self.__google_storage_client.close()


    def validate(self, arguments, data_lake_command):
        '''
            Validates the metadata
            Args:
                metadata: structure or file containing one or more patients
                    data
            Returns:
                boolean: True if all Patients have valid data, False if otherwise
        '''
        self.client_uuid        = arguments['client_id']
        self.arguments          = arguments
        self.data_lake_command  = data_lake_command
        json_structure          = Helpers.determine_json_structure(arguments['file_metadata'])
        self.metadata           = json_structure

        return self.__validate_metadata_json(json_structure)

    
    def __validate_metadata_json(self, metadata):
        '''
            Verifies that the json passed contains valid attributes
            Args:
                None
            Returns:
                boolean: True if the patient data is valid, False if otherwise
        '''
        for field in metadata:
            if field not in self.__metadata_validation_functions:
                continue
            if not self.__validate_field_in_metadata(field, metadata):
                return False

        return True


    def __validate_field_in_metadata(self, field, metadata):
        '''
            Validates a given fields in the patient data json structure using the mapping
            stored in the .__metadata_validation_functions dictionary
            Args:
                field           (string): The field we are going to validate
                patient_data    (dict): The dictionary of the patient data
            Returns:
                boolean: True if the field value is valid, False if otherwise
        '''
        return self.__metadata_validation_functions[field](metadata[field])
    

    def __validate_client(self, client):
        '''
            Validates the Client ID in the metadata
            Args:
                client (string): The client ID
            Returns:
                boolean: True, of the client is valid, False if otherwise
        '''
        if self.data_lake_command == 'file' and client == self.client_uuid:
            return True

        if self.data_lake_command == 'file update' and self.__check_if_bucket_exists(client):
            return True

        Helpers.print_error('Invalid CLIENT_ID' + client + IN_METADATA)
        return False


    def __check_if_bucket_exists(self, client):
        '''
            Checks if the client bucket exists, This only needs to be checked if we are
            switching patients' files between clients due to a messup
            Args:
                client (string): The client ID
            Returns:
                boolean: True, of the client is valid, False if otherwise
        '''
        bucket = self.__google_storage_client.bucket(client)
        result = Helpers.try_bucket_exists(bucket)

        if result:
            return True

        Helpers.print_error("datalake " + client + " does not exist: Bad Request")
        return False


    def __validate_patient_id(self, patient_id):
        '''
            Validates the Patient Id:
            Args:
                patient_id (string): The patient id
            Returns:
                boolean: True if the patient id is valid, False if otherwise
        '''
        expected_patient_id = Helpers.patient_hash(self.arguments['client_id'],
            [self.arguments['mrn']])[0]
        
        if patient_id != expected_patient_id:
            Helpers.print_error('Invalid PATIENT_ID ' + patient_id + IN_METADATA)
            return False

        return True


    def __validate_modality(self, modality):
        '''
            Validates the modality:
            Args:
                modality (string): The modality
            Returns:
                boolean: True if the modality is valid, False if otherwise
        '''
        if modality in Properties.Properties.instance().modalities:
            return True

        Helpers.print_error('Invalid MODALITY ' + modality + IN_METADATA)
        return False


    def __validate_file_path(self, gcs_file_path):
        '''
            Validates the gcs file path
            Args:
                gcs_file_path (string): the path in GCS where the file exists
            Returns:
                boolean: True if the file path matches with patient_id and
                    modality
        '''
        expected_patient_id = Helpers.patient_hash(self.arguments['client_id'], 
            [self.arguments['mrn']])[0]
        expected_file_path  = self.arguments['modality'] + '/' + expected_patient_id

        if gcs_file_path == expected_file_path:
            return True

        Helpers.print_error('file path ' + gcs_file_path + ' does not match the expected file path' + 
            expected_file_path + ' created from the arguments')
        return False


    # TO-DO update location of service validation after we know what to expect
    def __validate_location_of_service(self, location_of_service):
        '''
            validates the location of service
             Args:
                location_of_service (string): The location of service
            Returns:
                boolean: True if time of service is valide, false if otherwise
        '''
        return True


    # TO-DO update source validation after we know what to expect
    def __validate_source(self, source):
        '''
            validates the source
            Args:
                source (string): The source
            Returns:
                booleean: True if the source is valid, False if otherwise
        '''
        return True


    # TO-DO update originator validation after we know what to expect
    def __validate_originator(self, originator):
        '''
            validates the originator
            Args:
                source (string): The originator
            Returns:
                booleean: True if the originator is valid, False if otherwise
        '''
        return True


    def __validate_time_of_service(self, time_of_service):
        '''
            Validates the time of service
            Args:
                time_of_service (string): The data of service
            Returns:
                boolean: True if time of service is valide, false if otherwise
        '''
        if re.fullmatch(TIME_REGEX, time_of_service) is None:
            print(time_of_service + ' does not match time regex: not a valid time')
            return False

        #check valid time
        hour    = int(time_of_service[1:3])
        minute  = int(time_of_service[3:5])
        second  = int(time_of_service[5:7])

        if self.__is_valid_time(hour, minute, second):
            return True

        Helpers.print_error(time_of_service + ' is not a valid date')
        return False

    
    def __is_valid_time(self, hour, minute, second):
        '''
            checks if the year month and day creates a valid date
            Args:
                year    (string): The year
                month   (string): The month
                day     (string): the day
            Returns:
                boolean: True if a valid date is formed False if other wise
        '''
        try:
            datetime.time(hour, minute, second)
            return True
        except:
            return False

    