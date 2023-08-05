#
#   Created by Ryan McDermott
#   Created on 3/11/2022
#

import datetime

from google.cloud.bigquery_storage_v1 import types
from google.cloud.bigquery_storage_v1 import writer
from google.protobuf import descriptor_pb2

from indxdatalaketools.ClientTools.Changelog import changelog_schema_pb2
from indxdatalaketools import Helpers
from indxdatalaketools.GoogleClientWrappers import BigQuery


class Client:
    ''' Class that inserts data into the changelog table '''
    client_uuid                         = ''
    table_fields                        = ["CLIENT_ID","BUCKET_ID","FILE_PATH","FILE_NAME",
        "ACTION","ACTION_AT","REPLICATED","REPLICATED_AT"]

    __big_query_wrapper                 = None
    __google_big_query_storage_client   = None
    __proto_buf_dictionary              = None

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
        
        self.__google_big_query_storage_client  = google_clients.big_query_storage_v1_client
        self.__big_query_wrapper                = BigQuery.Wrapper(google_clients)

        self.__create_proto_buf_dictionary()

    def __create_proto_buf_dictionary(self):
        '''
            Function that creates the protobuf ditionary to use to populate 
            its attributes easily
        '''
        self.__proto_buf_dictionary = {
            "CLIENT_ID":        self.__insert_client_id, 
            "BUCKET_ID":        self.__insert_bucket_id,
            "FILE_PATH":        self.__insert_file_path,
            "FILE_NAME":        self.__insert_file_name,
            "ACTION":           self.__insert_action,
            "ACTION_AT":        self.__insert_action_at,
            "REPLICATED":       self.__insert_replicated,
            "REPLICATED_AT":    self.__insert_replicated_at
        }
        

    def insert_to_changelog_table(self, blob, action):
        ''' 
            Inserts information from an uploaded blob to the changelog table
            Args:
                blob (google.cloud.storage.Blob): The blob that was uploaded
            Returns:
                boolean: True if the data was inserted into the changelog table
        '''
        blob_data_dict  = self.__create_upload_dict(blob, action)
        dataset_id      = 'SNAPSHOTS_'+self.__transform_client_id()
        today           = self.__get_date_today()

        return self.__insert_data_to_changelog(dataset_id, today, blob_data_dict)


    def __create_upload_dict(self, blob, action):
        '''
            Creates a dictionary with all of the data for the table
            Args:
                blob   (google.cloud.storage.Blob): The blob that was 
                    created, updated, or deleted
                action (string): the action being taken
            Returns:
                dict: The dictionary containing all of the data
        '''
        time_now  = self.__get_datetime_now()

        client_id   = self.client_uuid
        bucket_id   = self.client_uuid
        file_path   = blob.metadata['FILE_PATH']
        file_name   = str(blob.name).split('/')[-1]
        action_at   = time_now
        replicated  = False

        return {'CLIENT_ID': client_id, 'BUCKET_ID':bucket_id, 'FILE_PATH':file_path,
            'FILE_NAME': file_name, 'ACTION':action, 'ACTION_AT': action_at, 
            'REPLICATED':replicated}
        

    def __get_datetime_now(self):
        '''
            Gets the current datetime for now and returns it
            Returns:
                datetime: The datetime of now
        '''
        now             = datetime.datetime.now()
        time_now_string = now.strftime('%Y-%m-%d %H:%M:%S')
        
        return time_now_string


    def __transform_client_id(self):
        '''
            Transforms the client id to contain no dashes and have all
            letters uppercase:
            Args:
                None
            Returns:
                string: transformed string
        '''
        client_id = self.client_uuid
        client_id = client_id.replace('-','')
        client_id = client_id.upper()

        return client_id


    def __get_date_today(self):
        '''
            creates a date string in YYYYMMDD format by using the date today 
            Returns:
                string: Date today in YYYYMMDD format
        '''
        today       = datetime.datetime.now()
        today_date  = today.date()
        today       = today_date.strftime('%Y%m%d')

        return str(today)


    def __insert_data_to_changelog(self, dataset_id, table_name, changelog_data):
        '''
            Function that inserts data into the changelog table
            Args:
                dataset_id        (string): The id of the data set
                table_name        (string): The name of the table
                changelog_data    (dict): The Patients Data
            Returns
                Boolean: True if the request worked, false if other wise
        '''
        parent                          = self.__google_big_query_storage_client\
            .table_path("indx-data-services", dataset_id, table_name)
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
        changelog_schema_pb2.changelog_schema_pb2.DESCRIPTOR.CopyToProto(proto_descriptor)
        proto_schema.proto_descriptor   = proto_descriptor
        proto_data                      = types.AppendRowsRequest.ProtoData()
        proto_data.writer_schema        = proto_schema
        request_template.proto_rows     = proto_data

        # Create a batch of row data by appending proto2 serialized bytes to the
        # serialized_rows repeated field.
        serialized_row  = self.__create_proto_buf_row(changelog_data)
        response_future_1 = self.__big_query_wrapper.insert_to_bq_table(
            self.__google_big_query_storage_client, serialized_row, request_template, stream_name, parent)
        
        if response_future_1.done():
            print('successfully inserted ' + str(changelog_data) + ' to CHANGELOG table')
            return True

        Helpers.print_error('Failed to insert ' + str(changelog_data) + ' to CHANGELOG table')
        return False


    def __create_proto_buf_row(self, protobuf_data):
        '''
            Creates protobuf object to be inserted into the data lake changelog table
            Args:
                protobuf_data (dict): The data we wish to insert
            returns
                serialized proto buf: The serialized proto buf object of the passed
                    dictionary
        '''
        row             = changelog_schema_pb2.changelog_schema_pb2()
        for field in self.table_fields:

            if field in protobuf_data:
                row = self.__proto_buf_dictionary[field](row, protobuf_data[field])

        return row.SerializeToString()


    def __insert_client_id(self, row, client_id):
        if client_id is None:
            return row
        row.CLIENT_ID = client_id
        return row


    def __insert_bucket_id(self, row, bucket_id):
        if bucket_id is None:
            return row
        row.BUCKET_ID = bucket_id
        return row


    def __insert_file_path(self, row, file_path):
        if file_path is None:
            return row
        row.FILE_PATH = file_path
        return row


    def __insert_file_name(self, row, file_name):
        if file_name is None:
            return row
        row.FILE_NAME = file_name
        return row


    def __insert_action(self, row, action):
        if action is None:
            return row
        row.ACTION = action
        return row


    def __insert_action_at(self, row, action_at):
        if action_at is None:
            return row
        row.ACTION_AT = action_at
        return row


    def __insert_replicated(self, row, replicated):
        if replicated is None:
            return row
        row.REPLICATED = replicated
        return row


    def __insert_replicated_at(self, row, replicated_at):
        if replicated_at is None:
            return row
        row.REPLICATED_AT = replicated_at
        return row
    