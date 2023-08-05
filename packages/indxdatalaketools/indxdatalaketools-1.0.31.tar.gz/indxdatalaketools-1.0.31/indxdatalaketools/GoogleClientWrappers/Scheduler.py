#
#   Created by Ryan McDermott
#   Created on 3/16/2022
#

from google.api_core.exceptions import NotFound
from indxdatalaketools import Helpers


class Wrapper:
    ''' Wrapper for all scheduler client API Calls'''
    __scheduler_client    = None


    def __init__(self, google_clients):
        self.__scheduler_client   = google_clients.cloud_scheduler_client


    def check_job_exists(self, job):
        '''
            Chekcs if the job already exists
            Args:
                job (dict): Dictionary of job request
            Returns:
                boolean: True if the job exists, False if otherwise
        '''
        try:
            self.__scheduler_client.get_job(request=job)
            return True
        except NotFound:
            return False


    def try_create_job(self, parent, job):
        ''' 
            Tries to create a cloud scheduler job
            Args:
                parent (google.cloud.scheduler_v1.types.Parent): The parent of the job
                job (google.cloud.scheduler_v1.types.Job): The job we wish to create
            Returns:
                boolean: True if the job was created False if otherwise
        '''
        try:
            self.__scheduler_client.create_job(request={
                "parent": parent,
                "job": job
            })
            print('Scheduled job was created')
            return True
        except Exception as exception:
            Helpers.print_error('Could not create cloud scheduler job: ' + str(exception))
            return False
