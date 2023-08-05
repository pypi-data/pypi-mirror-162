#
#   Created by Ryan McDermott
#   Created on 7/8/2022
#

from indxdatalaketools.PropertiesDBApi.PropertiesApi import Client

class Properties(object):
    properties_api = None
    modalities = []
    race_codes = []
    _instance = None
    

    def __init__(self):
        '''
            Should not be able to make a new instance of this singleton
        '''
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls,google_clients=None):
        '''
        singleton design pattern, call this function to get the singleton
        Args:
            cls (self@Properties): class of type self Properties
            google_clients (googleClients): The authentication to every google glient service
        Returns
            Properties: The properties singleton
        '''
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.properties_api = Client(google_clients)
            cls._instance.modalities = cls._instance.properties_api.get_modalities()
            cls._instance.race_codes = cls._instance.properties_api.get_race_codes()
            # Put any initialization here.
        return cls._instance


    def refresh_properties(self):
        '''
            Function that makes an api call to the properties DB API to refresh the property values
            found in the modalities and race codes.
        '''
        self.modalities = self.properties_api.get_modalities()
        self.race_codes = self.properties_api.get_race_codes()