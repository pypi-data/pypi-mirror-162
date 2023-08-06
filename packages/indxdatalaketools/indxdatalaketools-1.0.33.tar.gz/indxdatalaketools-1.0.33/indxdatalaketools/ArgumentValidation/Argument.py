#
#   Created By Ryan McDermott
#   Created on 2/18/2022
#

from pathlib import Path

from indxdatalaketools import Helpers
from indxdatalaketools.GoogleClientWrappers import CloudStorage
from indxdatalaketools.ArgumentValidation import PatientData
from indxdatalaketools.ArgumentValidation import ClientId
from indxdatalaketools.ArgumentValidation import FileMetadata
from indxdatalaketools.ArgumentValidation import ValidationHelpers
from indxdatalaketools.PropertiesDBApi import Properties


DOES_NOT_EXIST_BAD_REQUEST = " does not exist: Bad Request"


class Validator():
    '''
        Command line tool helper class to verify all command line arguments are
        valid
    '''
    arguments                       = {}
    data_lake_tool_command          = ''

    __argument_validation_functions = None
    __google_storage_client         = None
    __google_storage_wrapper        = None
    __patient_data_validator        = None
    __client_id_validator           = None
    __file_metadata_validator       = None


    def __init__(self, google_clients):
        '''
            Class that validates all arguments passed.
            Args:
                google_clients          (ApiClients): object containing all Google Api Clients
            Returns:
                None
        '''
        
        self.__google_storage_client    = google_clients.cloud_storage_client
        self.__google_storage_wrapper   = CloudStorage.Wrapper(google_clients)
        self.__patient_data_validator   = PatientData.Validator()
        self.__client_id_validator      = ClientId.Validator(google_clients)
        self.__file_metadata_validator  = FileMetadata.Validator(google_clients)
        self.__set_up_argument_validation_functions()


    def __set_up_argument_validation_functions(self):
        '''
            Sets up the dictionary containting all valid arguments and the 
            functions needed to validate them
        '''
        self.__argument_validation_functions = {
            'client_id':        self.__validate_client_id,
            'patient_data':     self.__validate_patient_data,
            'modality':         self.__validate_modality,
            'mrn':              self.__validate_mrn,
            'file_metadata':    self.__validate_file_metadata,
            'file_path':        self.__validate_file_path,
            'file_name':        self.__validate_file_name,
            'gsutil_uri':       self.__validate_gsutil_uri,
            'patient_id':       self.__validate_patient_id,
            'restore_date':     self.__validate_restore_date,
            'incremental_restore_date':     self.__validate_incremental_restore_date,
            'archive_bucket':   self.__validate_archive_bucket,
        }


    def close(self):
        '''
            Frees and destroys all allocated resources
            Returns:
                None
        '''
        self.__google_storage_client.close()
        self.__client_id_validator.close()
        self.__file_metadata_validator.close()
        

    def validate_all_arguments(self, arguments, data_lake_tool_command):
        '''
            Verifys all arguments passed, some arguments such as CLIENT_ID have 
            different validation checks depending on the command called
            Args:
                arguments               (dict): key/value pair of all arguments passed
                data_lake_tool_command  (string): The command called by the data lake tools
            Returns:
                boolean: True if all the arguments are valid, False if otherwise
        '''
        self.arguments                  = arguments
        self.data_lake_tool_command     = data_lake_tool_command

        for argument in arguments:
            if not self.__validate_argument(argument):
                return False

        return True


    def __validate_argument(self, argument):
        '''
            Validate a single argument based on they key passed
            Args:
                argument (string): The key of the argument for the arguments dictionary
            Returns:
                boolean: True if the argument is valid, False if otherwise
        '''
        return self.__argument_validation_functions[argument]()
        

    def __validate_client_id(self):
        '''
            Validates the client id argument, and exists in Datastore
            Args:
                None
            Returns:
                boolean: True if the client id is valid, False if otherwise
        '''
        return self.__client_id_validator.validate(self.arguments['client_id'], 
            self.data_lake_tool_command)


    def __validate_patient_data(self):
        '''
            Validates the patient data argument
            Args:
                None
            Returns:
                boolean: True if the patient data is valid, False if otherwise
        '''
        return self.__patient_data_validator.validate(
                self.arguments['patient_data'], self.arguments)


    def __validate_file_metadata(self):
        '''
            Validates the file metadata
            Args:
                None
            Returns:
                boolean: True if the modality is valid, False if otherwise
        '''
        return self.__file_metadata_validator.validate(
            self.arguments,
            self.data_lake_tool_command)
        

    def __validate_modality(self):
        '''
            Validates the modality
            Args:
                None
            Returns:
                boolean: True if the modality is valid, False if otherwise
        '''
        if self.arguments['modality'] in Properties.Properties.instance().modalities:
            return True

        Helpers.print_error('Incorrect modality ' + self.arguments['modality'])
        return False

    
    def __validate_mrn(self):
        '''
            Validates that the MRN only contains digits and letters
            Args:
                None
            Returns:
                boolean: True if the MRN is valid, False if otherwise
        '''
        if all(character.isalpha() or character.isdigit() or \
            character == '-' for character in self.arguments['mrn']):
            return True
        
        Helpers.print_error(self.arguments['mrn'] + \
            " is not a valid MRN: Does Not contain only letters, digits and hyphens")
        return False


    def __validate_patient_id(self):
        '''
            Validates the the patient id exists in the datalake
            Args:
                None
            Returns:
                boolean: True if the MRN is valid, False if otherwise
        '''
        patient_id  = self.arguments['patient_id']
        client_id   = self.arguments['client_id']
        for modality in Properties.Properties.instance().modalities:
            bucket      = self.__google_storage_client.get_bucket(client_id)
            blob_name   = modality + '/' + patient_id
            
            blob_list = list(bucket.list_blobs(prefix=blob_name))
            if len(blob_list)>0:
                return True

        print(patient_id + ' is not a valid patient id')
        return False


    def __validate_file_name(self):
        '''
            Validates the file name of a gcs_blob
            Args:
                None
            Returns:
                boolean: True if the file exists, False if otherwise
        '''
        patient_id          = Helpers.patient_hash(self.arguments['client_id'],
            [self.arguments['mrn']])[0]
        bucket_name         = self.arguments['client_id']
        source_blob_name    = self.arguments['modality'] + \
            '/' + patient_id + '/' + self.arguments['file_name']
        bucket              = self.__google_storage_client.bucket(bucket_name)
        blob                = bucket.blob(source_blob_name)
        
        result = Helpers.try_blob_exists(blob)
        if result:
            return True

        Helpers.print_error(source_blob_name + DOES_NOT_EXIST_BAD_REQUEST)
        return False
        

    def __validate_file_path(self):
        '''
            Validate the File Path
            Args:
                None
            Returns:
                boolean: True if the file path is valid False if other wise
        '''
        # gcs bucket
        if 'gs://' in self.arguments['file_path']:
            return self.__if_blob_exists(self.arguments['file_path'])

        # local file
        local_file_path = Path(self.arguments['file_path'])
        result =  local_file_path.is_file()
        
        if result:
            return True

        Helpers.print_error(self.arguments['file_path'] + DOES_NOT_EXIST_BAD_REQUEST)
        return False


    def __validate_gsutil_uri(self):
        '''
            Validates the gsutil uri
            Args:
                None
            Returns:
                boolean: True if the gsutil rui is valid
        '''
        return self.__if_blob_exists(self.arguments['gsutil_uri'])


    def __if_blob_exists(self, gcs_gsutil_uri):
        '''
            Checks if a gcs blob exists
            Args:
                gcs_gsutil_uri (string) gsutil uri of blob we want to upload
            Returns:    
                boolean: True if the blob exists, False if otherwise
        '''
        file_path           = gcs_gsutil_uri.replace("gs://", "")
        bucket_name         = file_path.split("/")[0]
        source_blob_name    = file_path.split("/", 1)[1]
        bucket              = self.__google_storage_client.bucket(bucket_name)
        blob                = bucket.blob(source_blob_name)

        result = Helpers.try_blob_exists(blob)
        if result:
            return True

        Helpers.print_error(source_blob_name + DOES_NOT_EXIST_BAD_REQUEST)
        return False

    def __validate_incremental_restore_date(self):
        '''
            Checks if a the provided restoration date is in the correct format and files exist for that date in the archive
            Args:
                None
            Returns:    
                boolean: True if the restoration date is valid, False if otherwise
        '''
        if not ValidationHelpers.validate_date(self.arguments['incremental_restore_date']):
            return False

        blob_list = self.__google_storage_client.list_blobs('indx-dummy-archive', prefix=self.arguments['client_id'] + '/' + self.arguments['incremental_restore_date'] + '/')
        if len(list(blob_list)) == 0:
            return False

        return True 

    def __validate_restore_date(self):
        ''' 
            Validates the restore date argument 
            returns:
                boolean: True if the restore date is valid, false if otherwise
        '''
        if not ValidationHelpers.validate_date(self.arguments['restore_date']):
            return False

        file_path   = 'PATIENTS_BACKUP/UNKNOWN'
        if len(self.__google_storage_wrapper.find_blobs_with_metadata(
            self.arguments['client_id'],
            'SNAPSHOT_DATE',
            self.arguments['restore_date'],
            path_prefix=file_path)) > 0:

            return True
        
        return False


    def __validate_archive_bucket(self):
        ''' 
            Validates the restore date argument 
            returns:
                boolean: True if the archive bucket exists, false if otherwise
        '''
        bucket_name = self.arguments['archive_bucket']
        if not self.__google_storage_wrapper.\
            check_if_bucket_exists(bucket_name):
            return False

        if bucket_name != 'indx-datalake-archives' and bucket_name != 'indx-dummy-archive':
            Helpers.print_error('archive bucket is not either indx-datalake-archives or indx-dummy-archive')
            return False

        return True