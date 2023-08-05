#
#   Created by Arjun Acharya
#   Created on 7/27/2022
#

from indxdatalaketools.GoogleClientWrappers import SecretManager
from indxdatalaketools import Helpers
import json

DOCUMENT_CLASSIFIER_URL = 'https://document-classifier-gateway-27i5vb12.uc.gateway.dev/'

class DocClassifierClient:
    '''
    Class that contains all the functionality make a call to Document Classifier
    '''
    __project_id                = ''
    __secret_id                 = ''
    __api_key                   = ''
    __secret_manager_wrapper    = None

    def __init__(self, google_clients):
        self.__project_id               = 'indx-data-services'
        self.__secret_id                = 'indx-document-classifier-api-key'
        self.__secret_manager_wrapper   = SecretManager.Wrapper(google_clients)
        self.__api_key                  = self.__secret_manager_wrapper.get_secret(self.__project_id, self.__secret_id)

    def get_modality_and_file_type(self, gcs_file_path):
        '''
            creates the request to the document classifier cloud run service
            args:
                gcs_file_path: str - gcs path of file on the staging bucket
            return:
                classified_modality: str - modality prediction made by the document classifier
                classified_file_type: str - file type prediction made by the document classifier
        '''
        headers = {"Content-Type": "application/json", "x-api-key":self.__api_key}
        payload = {"gcs_file_path" : gcs_file_path}
        data = json.dumps(payload)
        data = data.encode('utf-8')
        response = Helpers.create_post_request(DOCUMENT_CLASSIFIER_URL+"predict", headers=headers, body=data)
        classified_modality = response['modality']
        classified_file_type = response['file_type']

        return classified_modality, classified_file_type