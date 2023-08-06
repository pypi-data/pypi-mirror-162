#
#   Created By Ryan McDermott
#   Created On 2/17/2022
#
#   Top level file that hold all the logic for calling the executables. This
#   includes argument validations and implementing the sub modules for each 
#   command

import sys
import click
from google.cloud import storage
from indxdatalaketools import __version__
from indxdatalaketools.DataLakeOperations import DataLakeOps
from indxdatalaketools.DataLakeOperations import ArchiveServiceOps
from indxdatalaketools.DataLakeOperations import SnapshotOps
from indxdatalaketools.DataLakeFileOperations import PatientsTableOps
from indxdatalaketools.DataLakeFileOperations import FileOps
from indxdatalaketools.Helpers import print_error

@click.group()
@click.version_option(__version__)
def main():
    """ ALL DATA LAKE OPERATIONS """

#####
#   Data Lake Commands
#####
@main.group()
def datalake():
    """Commands for datalake operations"""


@datalake.command('create')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
def create(client_id, service_account):
    """\b\nCreates a datalake for a given Client ID and all supporting infrastrcuture

    Arguments: 

        CLIENT_ID:   The specific UUID4 for a client.
    """
    data_lake_client    = DataLakeOps.Client(client_id, service_account)
    result              = data_lake_client.create_data_lake()
    sys.exit(int(not result))

@datalake.command('restore')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('restore_date')
@click.argument('archive_bucket')
def restore_datalake(client_id, restore_date, archive_bucket, service_account):
    """\b\nRestores the datalake for a given Client ID up to a specified restore date

    Arguments: 

        CLIENT_ID:   The specific UUID4 for a client.
        RESTORE_DATE: The date in YYYYMMDD format
        ARCHIVE_BUCKET: The bucket you wish to restore from
    """
    
    archive_client    = ArchiveServiceOps.Client(client_id, service_account)
    data_lake_client  = DataLakeOps.Client(client_id, service_account)

    if not data_lake_client.create_data_lake():
        print_error('Failed to recreate datalake ' + client_id)
        sys.exit(1)
    
    result            = archive_client.restore_data_lake(restore_date, archive_bucket)
    sys.exit(int(not result))



#####
#   Snapshot Commands
#####
@main.group()
def snapshot():
    """Commands for datalake snapshot operations"""


@snapshot.command('datalake')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
def datalake_snapshot(client_id, service_account):
    """\b\nCreates a snapshot of the current specified datalake
    
    Arguments: 

        CLIENT_ID:   The specific UUID4 for a client.
    """
    # verify inputs
    snapshot_client     = SnapshotOps.Client(client_id, service_account)
    result              = snapshot_client.create_snapshot()
    sys.exit(int(not result))


@snapshot.command('patient')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('patient_id')
def datalake_patient_snapshot(client_id, patient_id, service_account):
    """\b\nCreates a snapshot of the current specified datalake
    
    Arguments: 
        CLIENT_ID:      The specific UUID4 for a client we wish to take a snapshot for
        PATIENT_ID:     The ID of the patient we wish to take a snapshot of
    """
    # verify inputs
    snapshot_client     = SnapshotOps.Client(client_id, service_account)
    result              = snapshot_client.create_patient_snapshot(patient_id)
    sys.exit(int(not result))


#####
#   PATIENTS Table Commands
#####
@main.group()
def patients_table():
    """Commands for PATIENTS table operations"""


@patients_table.command('upload')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('patient_data')
def upload_patient(client_id, patient_data, service_account):
    """\b\nuploads a single, or multiple patients to the PATIENTS table
    
    Arguments: 
        
        CLIENT_ID:      The specific UUID4 for a client.
        PATIENT_DATA:   The json string, or json file representing a single, or 
                        multiple patients. The json structure is
            PATIENT_ID:             String, UUID of patient 
            CLIENT_ID (REQUIRED):   String, UUID of client / health care agency 
            MRN (REQUIRED):         String, patient’s medical record number per the client’s EMR system 
            LASTNAME:               String, patient’s last name 
            FIRSTNAME:              String, patient’s first name 
            MIDDLENAME:             String, patient’s middle name 
            DOB:                    Date, patient’s date of birth 
            SEX:                    String, patient’s administrative gender as per the HL7 code 
            RACE:                   String, patient’s race as per the HL7 code 
    """
    patients_table_client   = PatientsTableOps.Client(client_id, service_account)
    result                  = patients_table_client.insert_patients(patient_data)
    sys.exit(int(not result))


@patients_table.command('update')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('patient_data')
def update_patient(client_id, patient_data, service_account):
    """\b\nuploads a single, or multiple patients to the PATIENTS table
    
    Arguments: 
        
        CLIENT_ID:      The specific UUID4 for a client.
        PATIENT_DATA:   The json string, or json file representing a single, or 
                        multiple patients. The json structure is
            PATIENT_ID:             String, UUID of patient 
            CLIENT_ID (REQUIRED):   String, UUID of client / health care agency 
            MRN (REQUIRED):         String, patient’s medical record number per the client’s EMR system 
            LASTNAME:               String, patient’s last name 
            FIRSTNAME:              String, patient’s first name 
            MIDDLENAME:             String, patient’s middle name 
            DOB:                    Date, patient’s date of birth 
            SEX:                    String, patient’s administrative gender as per the HL7 code 
            RACE:                   String, patient’s race as per the HL7 code 
    """
    patients_table_client   = PatientsTableOps.Client(client_id, service_account)
    result                  = patients_table_client.update_patients(patient_data)
    sys.exit(int(not result))


@patients_table.command('restore')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('restore_date')
def restore_table(client_id, restore_date, service_account):
    """\b\nuploads a single, or multiple patients to the PATIENTS table
    
    Arguments: 
        
        CLIENT_ID:      The specific UUID4 for a client.
        RESTORE_DATE:   The date you wish to restore the PATIENTS table to
    """
    patients_table_client   = PatientsTableOps.Client(client_id, service_account)
    result                  = patients_table_client.restore_table(restore_date)
    sys.exit(int(not result))


#####
#   File Commands
#####
@main.group()
def files():
    """Commands for file operations"""

@files.command('upload')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('modality')
@click.argument('mrn')
@click.argument('metadata')
@click.argument('file_path')
def upload_file(client_id, modality, mrn, metadata, file_path, service_account):
    """\b\nupload a file
    
    Arguments: 
        
        CLIENT_ID:      The specific UUID4 for a client.
        MODALITY:       The files MODALITY. acceptable parameters are:
            HVF
            OCT_RNFL
            OCT_RETINA
            AVS
        MRN:            The Patients medical record number
        METADATA:       The json string or json file of the file you wish to upload.
                        The structure is:
            CLIENT_ID (REQUIRED):   String, UUID of client / health care agency
            PATIENT_ID:             String, UUID of patient
            MODALITY:               String, The modality of the file
            FILE_PATH:              String, The path in the datalake where the file is stored
            DATE_OF_SERVICE:        String, The date of service in
            TIME_OF_SERVICE:        String, The time of service in
            LOCATION_OF_SERVICE:    String, Where the file was created
            SOURCE:                 String, The Source of the file
            ORIGINATOR:             String, The user that uploaded the file to the data lake
        FILE_PATH:      The path to the file you wish to upload
        
    """
    file_client     = FileOps.Client(client_id, credentials_file_path=service_account)
    result          = file_client.upload_file(modality, mrn, metadata, file_path)
    sys.exit(int(not result))


@files.command('delete')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('modality')
@click.argument('mrn')
@click.argument('file_name')
def delete_file(client_id, modality, mrn, file_name, service_account):
    """\b\ndelete a file
    
    Arguments: 
        
        CLIENT_ID:      The specific UUID4 for a client.
        MODALITY:       The files MODALITY. acceptable parameters are:
            HVF
            OCT_RNFL
            OCT_RETINA
            AVS
        MRN:            The Patients medical record number
        FILE_NAME:      The name of the file you wish to delete
        
    """
    file_client     = FileOps.Client(client_id, service_account)
    result          = file_client.delete_file(modality, mrn, file_name)
    sys.exit(int(not result))

@files.command('update')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('gsutil_uri')
@click.argument('metadata')
def update_file(client_id, gsutil_uri, metadata, service_account):
    """\b\nupdate a file's metadata
    
    Arguments: 
        
        CLIENT_ID:      The specific UUID4 for a client.
        GSUTIL_URI:     The gsutil uri of the blob you wish to update
        METADATA:       The json string or json file of the file you wish to upload.
                        The structure is:
            CLIENT_ID (REQUIRED):   String, UUID of client / health care agency
            PATIENT_ID:             String, UUID of patient
            MODALITY:               String, The modality of the file
            FILE_PATH:              String, The path in the datalake where the file is stored
            DATE_OF_SERVICE:        String, The date of service in
            TIME_OF_SERVICE:        String, The time of service in
            LOCATION_OF_SERVICE:    String, Where the file was created
            SOURCE:                 String, The Source of the file
            ORIGINATOR:             String, The user that uploaded the file to the data lake
        
    """
    file_client     = FileOps.Client(client_id, service_account)
    result          = file_client.update_file_metadata(gsutil_uri, metadata)
    sys.exit(int(not result))



#####
#   File Commands
#####
@main.group()
def patients():
    """Commands for patient operations"""

@patients.command('delete')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('mrn')
def delete_patient(client_id, mrn, service_account):
    """\b\ndelete a file
    
    Arguments: 
        
        CLIENT_ID:      The specific UUID4 for a client.
        MRN:            The Patients medical record number
        
    """
    file_client     = FileOps.Client(client_id, service_account)
    result          = file_client.delete_patient(mrn)
    sys.exit(int(not result))


@patients.command('restore')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('restore_date')
@click.argument('archive_bucket')
@click.argument('mrn')
def restore_patient(client_id, restore_date, archive_bucket, mrn, service_account):
    """\b\nrestore a patient to the specified date in time
    
    Arguments: 
        
        CLIENT_ID:      The specific UUID4 for a client.
        RESTORE_DATE: The date in YYYYMMDD format
        ARCHIVE_BUCKET: The specified archive bucket used for restoration
        MRN:            The Patients medical record number
    
    """
    
    archive_client    = ArchiveServiceOps.Client(client_id, service_account)
    result            = archive_client.restore_patient(restore_date, archive_bucket, mrn)
    sys.exit(int(not result))


@patients.command('delete-from-archive')
@click.option('--service_account', default=None, help='The path to the service account key json file')
@click.argument('client_id')
@click.argument('archive_bucket')
@click.argument('mrn')
def delete_patient_from_archive(client_id, archive_bucket, mrn, service_account):
    """\b\ndelete a patient from the specified archive bucket

    Arguments: 
        
        CLIENT_ID:      The specific UUID4 for a client.
        ARCHIVE_BUCKET: The specified archive bucket used for restoration
        MRN:            The Patients medical record number
    
    """
    
    archive_client    = ArchiveServiceOps.Client(client_id, service_account)
    result            = archive_client.delete_patient_in_archive(archive_bucket, mrn)
    sys.exit(int(not result))

if __name__ == '__main__':
    main()