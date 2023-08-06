#
#   Created by Ryan McDermott
#   Created on  2/24/2022
#

import re
import sys
import cv2

import numpy as np

from indxdatalaketools import Helpers
from indxdatalaketools.ClientTools.PatientsTable import Insert
from indxdatalaketools.ClientTools.Changelog import Insert as ChnglogInsert
from indxdatalaketools.DataStandardizer import PatientTable


class Client:
    '''
        Class that contains all the functionality to upload a file
        to a data lake
    '''

    client_uuid                         = ''
    text_file_list                      = ["txt", "tsv", "csv"]

    __google_storage_client             = None
    __patients_table_client             = None
    __changelog_client                  = None
    __data_standardizer                 = None

    def __init__(self, google_clients, client_uuid):
        '''
            Init function that sets up client credentials, uuid, 
            and google api clients used to upload files to a GCS bucket
            Args:
                google_clients          (ApiClients): object containing all Google Api Clients
                client_uuid             (string): The client's uuid
            Returns:
                None
        '''
        self.client_uuid                = client_uuid
        self.__google_storage_client    = google_clients.cloud_storage_client
        self.__patients_table_client    = Insert.Client(
            google_clients, self.client_uuid)
        self.__changelog_client         = ChnglogInsert.Client(
            google_clients, self.client_uuid)
        self.__data_standardizer        = PatientTable.Client()
                

    def close(self):
        '''
            Frees and destroys all allocated resources
            Returns:
                None
        '''
        self.__google_storage_client.close()
        self.__patients_table_client.close()


    def upload_file_to_datalake(self, modality, mrn, metadata, file_path):
        '''
            Uploads a file to the data lake and sets the metadata
            for that file
            Args:
                modality    (string): The file's modality
                mrn         (string): The mrn of the patient to who the files belongs to
                metadata    (string): The metadata that is associated with the
                    file
                file_path   (string): The path to the file we wish to upload to a 
                    datalake
            Returns:
                boolean: True if the File was successfully uploaded, False if 
                    otherwise
                
        '''
        file_contents       = self.__read_file_contents(file_path)

        # convert bmp to png
        if '.bmp' in file_path.lower():
            file_contents = self.__convert_bmp_to_png(file_contents)
            file_path = file_path.replace(file_path[len(file_path) - 3:], 'png')

        stripped_mrn        = self.__strip_leading_zeros(mrn)
        hashed_patient_mrn  = Helpers.patient_hash(self.client_uuid, [stripped_mrn])[0]
        hashed_file_name    = Helpers.hash_contents_to_file_name(file_path, file_contents)
        blob_name           = modality + "/" + hashed_patient_mrn + "/" + hashed_file_name
        bucket              = self.__google_storage_client.bucket(self.client_uuid)
        blob                = bucket.blob(blob_name)

        if Helpers.try_blob_exists(blob):
            Helpers.print_error("File" + blob.name + " already exists")
            return False

        if not self.__create_blob_with_metadata(blob, file_contents, metadata):
            Helpers.print_error("Could not upload file " + file_path + " to datalake")
            return False

        if hashed_patient_mrn != 'UNKNOWN'and \
            not self.__insert_data_to_patients_table(stripped_mrn, hashed_patient_mrn):
            Helpers.print_error("Could not insert data to PATIENTS table")
            return False

        blob.metadata = metadata
        return self.__changelog_client.insert_to_changelog_table(blob, 'CREATED')


    def __convert_bmp_to_png(self, file_bytes):
        '''
            Converts the BMP bytes string into a png bytes string
            Args:
                byte (string): The string of bytes we wish to convert
            Returns:
                string: The converted bytes in string format
        '''
        nparr       = np.frombuffer(file_bytes, dtype=np.uint8)
        img         = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        png_img     = cv2.imencode('.png', img)[1]
        data_encode = np.array(png_img)
        byte_encode = data_encode.tobytes()

        return byte_encode


    def __strip_leading_zeros(self, string_to_strip):
        '''
            strips the leading '0' from a string
            Args:
                string_to_strip (string): Te string we wish to strip
            Returns:
                string: The string with leading '0' stripped
        '''
        stripped_string = re.sub("^0+", "", string_to_strip)

        return stripped_string

    
    def __insert_data_to_patients_table(self, mrn, hashed_patient_mrn):
        '''
            Inserts the file's patient to the patient table
            Args:
                mrn (string): the patients mrn
                hashed_patient_mrn (stirng): the patient id
        '''
        patient_data = {"MRN":mrn, 
                        "CLIENT_ID":self.client_uuid,
                        "PATIENT_ID":hashed_patient_mrn
                        }

        patient_data = self.__data_standardizer.standardize(patient_data)
            
        if self.__patients_table_client.insert_data_to_patients_table(patient_data):
            return True

        Helpers.print_error('Failed to upload ' + str(patient_data) + ' to patients table')
        return False


    def __create_blob_with_metadata(self, blob, file_contents, metadata):
        '''
            Creates the blob in GCS and adds metadata to it
            Args:
                blob (google.cloud.storage.blob): The blob we want to upload
                file_contents (bytes): The bytes of the file we wish to upload
                metadata (dict): The files Metadata
            Returns:
                boolean: True if the operation was successful, False if otherwise
        '''
        # add metadata to blob and save in bucket
        blob.metadata = metadata
        
        if not self.__try_upload_blob(blob, file_contents):
            return False

        if Helpers.try_blob_exists(blob):
            print('successfully uploaded file to datalake')
            return True

        return False


    def __read_file_contents(self, file_path):
        """
            Reads file from the file path, has the capabilities to read from local file,
            network file, and url. The file will be decoded to UTF-8 and remove carraige returns
            "\r" to match LF encoding.

            Args:
                file_path: The local file path, server file path or url
            Returns:
                string: string representation of data found
        """
        
        extension       = file_path.split("/")[-1].split(".")[-1].lower()

        if "gs://" in file_path:
            # GCS BUCKET
            if extension in self.text_file_list:
                content = self.__read_gcs_blob(file_path)
                return content.replace(b'\r\n', b'\n')
            else:
                file_bytes = self.__read_gcs_blob(file_path)
                return file_bytes
        
        # LOCAL FILE
        if extension in self.text_file_list:
            content = open(file_path, 'rb').read()
            return content.replace(b'\r\n', b'\n')
        else:
            file_bytes = open(file_path, 'rb').read()
            return file_bytes
    

    def __read_gcs_blob(self, gcs_blob_path):
        '''
            Reads a blob from GCS and returns the bytes 
            Args:
                gcs_blob_path (string): The path to the blob
            Returns:
                bytes: contents of the gcs blob
        '''
        file_path           = gcs_blob_path.replace("gs://", "")
        bucket_name         = file_path.split("/")[0]
        source_blob_name    = file_path.split("/", 1)[1]
        extension           = file_path.split("/")[-1].split(".")[-1].lower()
        bucket              = self.__google_storage_client.bucket(bucket_name)
        blob                = bucket.blob(source_blob_name)

        content = blob.download_as_bytes()

        return content

    def __try_upload_blob(self, blob, contents):
        '''
            Tries to upload a blob to GCS with string contents
            Args:
                blob (google.cloud.storage.Blob): The blob we wish to upload to
                contents (string): The files contents
        '''
        try:
            blob.upload_from_string(contents)
            return True
        except Exception as e:
            Helpers.print_error("Could not upload blob " + str(e))
            sys.exit(1)