#
#   Created by Ryan McDermott
#   Created on 2/21/2022
#

import datetime
import sys
from google.cloud.bigquery_storage_v1 import types
from google.protobuf import descriptor_pb2

from indxdatalaketools.ClientTools.PatientsTable import table_schema_pb2
from indxdatalaketools.ClientTools.PatientsTable import Update
from indxdatalaketools import Helpers
from indxdatalaketools.GoogleClientWrappers import BigQuery

class Client:
    '''
        Class that contains all the functionality to insert a patient into
        The patient table
    '''

    client_uuid                         = ''
    dataset_id                          = ''
    patient_table_name                  = ''
    table_fields                        = ["CLIENT_ID","MRN","PATIENT_ID","FIRSTNAME",
            "MIDDLENAME","LASTNAME","DOB","SEX","RACE", 'CHECKSUM','UPDATED_AT']

    __proto_buf_dictionary              = None
    __google_big_query_client           = None
    __google_big_query_storage_client   = None
    __big_query_wrapper                 = None
    __patient_table_update_client       = None

    def __init__(self, google_clients, client_uuid):
        '''
            Init function that sets up client credentials, uuid, 
            and google api clients used to insert items to the Patients table
            Args:
                google_clients          (ApiClients): object containing all Google Api Clients
                client_uuid             (string): The client's uuid
            Returns:
                None
        '''
        self.client_uuid                        = client_uuid
        self.dataset_id                         = self.client_uuid.replace("-", "_")
        self.patient_table_name                 = 'indx-data-services.' + \
            self.dataset_id + ".PATIENTS"
        self.__google_big_query_client          = google_clients.big_query_client
        self.__google_big_query_storage_client  = google_clients.big_query_storage_v1_client
        self.__patient_table_update_client      = Update.Client(google_clients, client_uuid)
        self.__big_query_wrapper                = BigQuery.Wrapper(google_clients)
        self.__create_proto_buf_dictionary()

    def __create_proto_buf_dictionary(self):
        '''
            Function that creates the protobuf ditionary to use to populate 
            its attributes easily
        '''
        self.__proto_buf_dictionary = {
            "CLIENT_ID":    self.__insert_client_id, 
            "MRN":          self.__insert_mrn,
            "PATIENT_ID":   self.__insert_patient_id,
            "FIRSTNAME":    self.__insert_first_name,
            "MIDDLENAME":   self.__insert_middle_name,
            "LASTNAME":     self.__insert_last_name,
            "DOB":          self.__insert_dob,
            "SEX":          self.__insert_sex,
            "RACE":         self.__insert_race,
            "CHECKSUM":     self.__insert_checksum,
            "UPDATED_AT":   self.__insert_updated_at,
        }


    def close(self):
        '''
            Frees and destroys all allocated resources
            Returns:
                None
        '''
        self.__google_big_query_client.close()
        self.__patient_table_update_client.close()
    

    def insert_data_to_patients_table(self, patient_json, overwrite=False):
        '''
            This function determines whether the patient_json is a list
            or a single patient. Then it uploads all patient data to the PATIENT 
            table for the client_id
            Args:
                patient_json    (json): Either a json object or a JSON Array containing
                    multiple patients data
                overwrite       (boolean): Flag to indicat whether or not we can overwrite the patients 
                    data
            Returns: 
                boolean: True if the patient/s were succesfully inserted in the PATIENTS table
        '''
        # parse json to determine single or multiple patients
        
        # multiple patients
        if isinstance(patient_json, list):
            return self.__insert_multiple_patients_to_table(patient_json)
        
        return self.__insert_patient_to_patients_table(patient_json, overwrite=overwrite)
                
    
    def __insert_multiple_patients_to_table(self, json_structure, overwrite=False):
        '''
            loops through json structure and inserts all patients into the PATIENTS
            table
            Args:
                json_structure (dict[]): list of dictionarys containing the patients data
                overwrite (boolean): Flag to indicate whether or not the row needs to get
                    overwritten
            Returns:
                boolean: True if the operation was a success False if otherwise
        '''
        for i in json_structure:
            if self.__insert_patient_to_patients_table(i, overwrite=overwrite):
                continue
            else:
                Helpers.print_error("could not upload " + str(i) +
                " to the PATIENTS table")
                return False
        return True


    def __insert_patient_to_patients_table(self, patient_data, overwrite=False):
        '''
            Function that adds a single patient to the patient table, if that patient already exists
            in the table their data is updated with the provided information
            Args:
                patient_data    (dict): The data we wish to add to the patient table
                overwrite       (boolean): Flag to indicate whether or not we can over 
                    write the patients data
            Returns:
                boolean: True if the operation was a success, false if otherwise
        '''
        now                         = datetime.datetime.now()
        patient_data['UPDATED_AT']  = str(now)
        print(patient_data)
        patient_mrn                 = patient_data['MRN']
        patient_id                  = Helpers.patient_hash(self.client_uuid, [patient_mrn])[0]
        patient_row                 = self.__get_patient_in_patients_table(patient_mrn, patient_id)
        
        return self.__insert_data_to_patients_table(patient_data, patient_row, overwrite)


    def __get_patient_in_patients_table(self, patient_mrn, patient_id):
        '''
            performs a query look up on the PATIENTS table to find if the given patient
            exists in the PATIENTS table
            Args:
                patient_mrn (string): The patients mrn
                patient_id  (string): The patients UUID
            Returns:
                The row of the Patient, if they are not in the table None is returned
        '''
        query       = 'SELECT * \
                    FROM `'+self.patient_table_name+'`\
                    WHERE MRN =\'' + patient_mrn +'\'\
                    AND PATIENT_ID =\'' +patient_id + '\''
        rows        = self.__big_query_wrapper.perform_query(query)

        if rows is None:
            return None

        if rows.total_rows == 0:
            return None
        if rows.total_rows > 1:
            Helpers.print_error("CRITICAL: Error in PATIENTS table, multiple instances of MRN: " + patient_mrn +
            " and PATIENT_ID " + patient_id)
            sys.exit(1)

        # must only contain one row if not 0 and > 1
        for row in rows:
            return row    


    def __insert_data_to_patients_table(self, patient_data, patient_row, overwrite=False):
        '''
            Inserts data to the patients table, if the data needs to be updated it will overwrite
            if the flag is set
            Args:
                patient_data (dict): The dictionary of the patients data
                patient_row  (row): The row already existing in the patients table
                overwrite    (boolean): True if we wish to overwrite the existing data in the 
                    PATIENTS table
            Returns:
                boolean: True if the operations was successful, False if otherwise
        '''
        if patient_row is not None:
            # patient exists, updated patient in table
            return self.__patient_table_update_client.update_patient_in_patient_table(
                patient_data, patient_row, overwrite=overwrite)
        elif overwrite == False:               
            # if not append to PATIENTS table
            return self.__add_data_to_patient_table(patient_data)
        else:
            Helpers.print_error("patient does not exist cannot update")
            return False


    def __add_data_to_patient_table(self, patient_data):
        '''
            Adds the patients data to the PATIENT table using the Big Query 
            Storage API COMMITTED row type to bypass the streaming buffer
            Args:
                patient_data    (dict): The Patients Data
            Returns
                Boolean: True if the request worked, false if other wise
        '''
        parent                          = self.__google_big_query_storage_client\
            .table_path("indx-data-services", self.dataset_id, "PATIENTS")
        write_stream                    = types.WriteStream()
        write_stream.type_              = types.WriteStream.Type.COMMITTED
        write_stream                    = self.__google_big_query_storage_client\
            .create_write_stream(
            parent=parent, write_stream=write_stream
        )
        stream_name                     = write_stream.name

        # Create a template with fields needed for the first request.
        request_template                = types.AppendRowsRequest()

        # The initial request must contain the stream name.
        request_template.write_stream   = stream_name

        # So that BigQuery knows how to parse the serialized_rows, generate a
        # protocol buffer representation of your message descriptor.
        proto_schema                    = types.ProtoSchema()
        proto_descriptor                = descriptor_pb2.DescriptorProto()
        table_schema_pb2.table_schema_pb2.DESCRIPTOR.CopyToProto(proto_descriptor)
        proto_schema.proto_descriptor   = proto_descriptor
        proto_data                      = types.AppendRowsRequest.ProtoData()
        proto_data.writer_schema        = proto_schema
        request_template.proto_rows     = proto_data

        # Create a batch of row data by appending proto2 serialized bytes to the
        # serialized_rows repeated field.
        
        serialized_row  = self.__create_proto_buf_row(patient_data)
        response_future_1 = self.__big_query_wrapper.insert_to_bq_table(
            self.__google_big_query_storage_client, serialized_row, request_template, stream_name, parent)
        
        if response_future_1.done():
            print('successfully inserted ' + str(patient_data) + ' to PATIENTS table')
            return True

        Helpers.print_error('Failed to insert ' + str(patient_data) + ' to PATIENTS table')
        return False
            
    
    def __create_proto_buf_row(self, patient_data):
        '''
            Creates a protobuf table_schema object to insert into a
            BQ table
            Args:
                patient_data (dict): Dictionary containing patient data
            Returns:
                serialized proto buf: The serialized proto buf object of the passed
                    dictionary
        '''
        row             = table_schema_pb2.table_schema_pb2()
        for field in self.table_fields:

            if field in patient_data:
                row = self.__proto_buf_dictionary[field](row, patient_data[field])

        return row.SerializeToString()
        
        
    def __insert_client_id(self, row, client_id):
        if client_id is None:
            return row
        row.CLIENT_ID = client_id
        return row

    def __insert_mrn(self, row, mrn):
        if mrn is None:
            return row
        row.MRN = mrn
        return row

    def __insert_patient_id(self, row, patient_id):
        if patient_id is None:
            return row
        row.PATIENT_ID = patient_id
        return row

    def __insert_first_name(self, row, first_name):
        if first_name is None:
            return row
        row.FIRSTNAME = first_name
        return row

    def __insert_middle_name(self, row, middle_name):
        if middle_name is None:
            return row
        row.MIDDLENAME = middle_name
        return row

    def __insert_last_name(self, row, last_name):
        if last_name is None:
            return row
        row.LASTNAME = last_name
        return row

    def __insert_dob(self, row, dob):
        if dob is None:
            return row

        dob     = dob.split("-")
        year    = int(dob[0])
        month   = int(dob[1])
        day     = int(dob[2])
        date    = datetime.datetime(year, month, day, 0, 0).timestamp()
        row.DOB = int(date)
        return row
    
    def __insert_sex(self, row, sex):
        if sex is None:
            return row
        row.SEX = sex
        return row

    def __insert_race(self, row, race):
        if race is None:
            return row
        row.RACE = race
        return row

    def __insert_checksum(self, row, checksum):
        if checksum is None:
            return row
        row.CHECKSUM = checksum
        return row

    def __insert_updated_at(self, row, updated_at):
        if updated_at is None:
            return row
        row.UPDATED_AT = updated_at
        return row