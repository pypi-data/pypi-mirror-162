#
#   Created by Ryan McDermott
#   Created on 2/25/2022
#

from indxdatalaketools import Helpers

class Standardizer():
    ''' Class that standardizes the file metadata dictionary '''
    arguments = {}


    def __init__(self, arguments):
        self.arguments = arguments

    
    def standardize(self, file_metadata):
        '''
            Standardizes the file metadata passed by the client, This includes adding the 
            modality, patient id, client id and file path if they do not exist
            Args:
                file_metadata (dict): the file metadata
            Returns:
                dict: The updated/standardized file metadata
        '''
        json_structure  = Helpers.determine_json_structure(file_metadata)
        file_metadata   = self.__populate_missing_fields(json_structure)
        file_metadata   = self.__set_missing_fields_to_unknown(file_metadata)

        return file_metadata
    

    def __populate_missing_fields(self, file_metadata):
        '''
            Populates the required metadata fields if they do not exist. These fields are
             modality, patient id, client id and file path
             Args:
                file_metadata (dict): The file metadata
            Returns:
                dict: updated file metadata
        '''
        if 'CLIENT_ID' not in file_metadata:
            file_metadata['CLIENT_ID'] = str(self.arguments['client_id'])

        if 'MODALITY' not in file_metadata:
            file_metadata['MODALITY'] = str(self.arguments['modality'])

        if 'PATIENT_ID' not in file_metadata:
            if self.arguments['mrn'] == 'UNKNOWN':
                file_metadata['PATIENT_ID'] = 'UNKNOWN'
            else:
                file_metadata['PATIENT_ID'] = Helpers.patient_hash(self.arguments['client_id'],
                [self.arguments['mrn']])[0]

        if 'FILE_PATH' not in file_metadata:
            file_metadata['FILE_PATH'] = str(file_metadata['MODALITY']) + \
            '/' + str(file_metadata['PATIENT_ID'])

        return file_metadata


    def __set_missing_fields_to_unknown(self, file_metadata):
        '''
            Sets any non-required missing fields to UNKOWN
            Args:
                file_metadata (dict): dictioary containing file metadata
            Retruns:
                dict: Updated file metadata
        '''
        optional_fields = ['DATE_OF_SERVICE', 'TIME_OF_SERVICE' ,'LOCATION_OF_SERVICE', 'SOURCE', 'ORIGINATOR']
        for field in optional_fields:
            if field not in file_metadata:
                file_metadata[field] = 'UNKNOWN'

        return file_metadata
