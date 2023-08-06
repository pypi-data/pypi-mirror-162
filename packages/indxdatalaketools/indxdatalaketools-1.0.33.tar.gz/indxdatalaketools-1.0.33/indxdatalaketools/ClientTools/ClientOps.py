#
#   Created by Ryan McDermott
#   Created on 5/12/2022
#

from indxdatalaketools import GoogleClients
from indxdatalaketools.PropertiesDBApi import Properties
from indxdatalaketools.ArgumentValidation import Argument

from indxdatalaketools.DataStandardizer import FileMetadata, PatientTable
from indxdatalaketools.ClientTools.Files import Upload
from indxdatalaketools.ClientTools.PatientsTable import Insert
from indxdatalaketools.DocumentClassifierApi import DocumentClassifierApi
from indxdatalaketools.GoogleClientWrappers import CloudStorage
from indxdatalaketools import Helpers
import warnings

class Client:

    client_uuid                         = ''

    __argument_validator                = None
    __google_clients                    = None
    __upload_file                       = None

    def __init__(self, client_uuid, credentials_file_path=None):
        '''
            Init function that sets up client credentials, uuid, 
            and File operations API
            Args:
                credentials_file_path   (string): The path to a Service Account key json file
                client_uuid             (string): The client's uuid
            Returns:
                None
        '''
        self.client_uuid                = client_uuid

        self.__google_clients           = GoogleClients.ApiClients(credentials_file_path)
        self.__argument_validator       = Argument.Validator(self.__google_clients)
        self.__upload_file              = Upload.Client(self.__google_clients, client_uuid)
        self.__insert_patient           = Insert.Client(self.__google_clients, client_uuid)
        self.__document_classifier      = DocumentClassifierApi.DocClassifierClient(self.__google_clients)
        self.__cloud_storage_wrapper    = CloudStorage.Wrapper(self.__google_clients)


    def upload_file(self, modality, mrn, metadata, file_path):
        '''
            Top level function that uploads a file to a Datalake, This will aslo add the 
            Patient data to the PATIENTS table if applicable
            Args:
                modality    (string): The modality of the file
                mrn         (string): The mrn of who the file belongs to
                metadata    (dict|string|file_path): Any metadata belonging to the file
                file        (string): The file path of the file we wish to upload
            Returns:
                boolean: True if the operation was a success, False if otherwise
        '''
        # validate arguments
        arguments           = {
            'client_id':self.client_uuid, 
            'modality':modality,
            'mrn':mrn,
            'file_metadata':metadata,
            'file_path':file_path}
        data_lake_command   = 'file'
        
        Properties.Properties.instance(self.__google_clients)

        if not self.__argument_validator.validate_all_arguments(arguments, data_lake_command):
            return False

        # standardize the metadata
        file_metadata_standardizer = FileMetadata.Standardizer(arguments)
        file_metadata = file_metadata_standardizer.standardize(metadata)

        # run the document classifier, check if modality matches predicted modality
        classified_modality = self.__document_classifier_operations(mrn, file_path)
        if not classified_modality:
            warnings.warn("Request to document classifier failed.")
        elif classified_modality != modality:
            Helpers.print_error("Modality may be incorrect. Modality might be " + classified_modality)

        # run command
        return self.__upload_file.upload_file_to_datalake(
            modality, mrn, file_metadata, file_path)


    def __document_classifier_operations(self, mrn, file_path):
        '''
            function that handles operations required to run the document classifier. This includes uploading file from local to 
            a staging folder on the clients data lake, running the document classifier with this uploaded blob and then deleting the blob
            args:
                mrn: str - input mrn
                file_path: str - local file path of input file
            return:
                classified_modality: str - modaity prediction of the document classifier
        '''
        blob = self.__cloud_storage_wrapper.upload_local_file_to_gcs_bucket(mrn, file_path, "staging_folder", self.client_uuid)
        if not blob:
            return blob

        gcs_file_path = "gs://"+blob.bucket.name+"/"+blob.name
        classified_modality, classified_file_type = self.__send_request_to_document_classifier(gcs_file_path)
        
        result = Helpers.delete_blob(blob)
        if not result:
            warnings.warn("Error faced when trying to delete blob from staging_folder")
        return classified_modality
        

    def __send_request_to_document_classifier(self, gcs_file_path):
        '''
            runs the document classifier
            args:
                gcs_file_path: str gcs path of file in staging folder
            return:
                classified_modality: str - modality prediction of the document classifier
                classified_file_type: str - file type prediction of the document classifier
        '''
        try:
            return self.__document_classifier.get_modality_and_file_type(gcs_file_path)
        except Exception as e:
            print("Error when trying to run document classifier. " + str(e))
            return False, False
        

    def upload_patient(self, patient_data):
        '''
            Top level function that uploads a patient to a PATIENT table, This will also update missing
            patient data but not overwrite it.
            Args:
                patient_data (dict): Dictionary containing the data to insert a patient to the patient table
            Returns:
                boolean: True if the operation was a success, False if otherwise
        '''
        # verify inputs
        arguments           = {'client_id':self.client_uuid, 'patient_data':patient_data}
        data_lake_command   = 'patients-table'

        Properties.Properties.instance(self.__google_clients)

        if not self.__argument_validator.validate_all_arguments(arguments, data_lake_command):
            return False

        # clean data
        data_standardizer   = PatientTable.Client()
        patient_data        = data_standardizer.standardize(patient_data)

        # run the command
        return self.__insert_patient.insert_data_to_patients_table(patient_data)